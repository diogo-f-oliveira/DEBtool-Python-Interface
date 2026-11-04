"""HTTP client for listing and downloading files from the Add-my-Pet website."""

from __future__ import annotations

import os
from email.utils import formatdate, parsedate_to_datetime
from enum import Enum
from html.parser import HTMLParser
from pathlib import Path
from typing import Mapping

import requests
from requests.adapters import HTTPAdapter

from .urls import AMP_BASE_URL, ampdata_file_url, species_dir_url, species_file_url


class DownloadStatus(str, Enum):
    """Outcome of a single file download."""

    DOWNLOADED = "downloaded"
    UPDATED = "updated"
    NOT_MODIFIED = "not_modified"
    SKIPPED_EXISTS = "skipped_exists"
    FAILED = "failed"


class _ListingParser(HTMLParser):
    """Collects the href of every anchor in an Apache directory listing."""

    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag, attrs) -> None:
        if tag != "a":
            return
        href = dict(attrs).get("href")
        if href:
            self.hrefs.append(href)


def parse_directory_listing(html: str, *, include_dirs: bool = True, include_files: bool = True) -> list[str]:
    """Return the entries of an Apache directory listing page.

    Sorting links (``?C=N;O=D``), absolute links such as the parent directory and external links are skipped.
    Directory entries keep their trailing ``/``.
    """
    parser = _ListingParser()
    parser.feed(html)
    entries = []
    for href in parser.hrefs:
        if href.startswith(("?", "/", "#")) or "://" in href:
            continue
        is_dir = href.endswith("/")
        if (is_dir and not include_dirs) or (not is_dir and not include_files):
            continue
        entries.append(href)
    return entries


def _is_species_estimation_file(file_name: str) -> bool:
    # Result figures and html pages are skipped, the results .mat file is kept
    return not file_name.startswith("results") or file_name.endswith(".mat")


class AmPClient:
    """Thin wrapper around a pooled ``requests.Session`` pointed at the AmP website.

    The same client can be shared between threads to download several species concurrently.
    """

    def __init__(
            self,
            *,
            base_url: str = AMP_BASE_URL,
            timeout: float = 60.0,
            max_retries: int = 3,
            pool_size: int = 50,
            session: requests.Session | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        if session is None:
            session = requests.Session()
            adapter = HTTPAdapter(pool_connections=pool_size, pool_maxsize=pool_size, max_retries=max_retries)
            session.mount("https://", adapter)
            session.mount("http://", adapter)
        self.session = session

    def list_directory(self, url: str, *, include_dirs: bool = True, include_files: bool = True) -> list[str]:
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return parse_directory_listing(response.text, include_dirs=include_dirs, include_files=include_files)

    def list_species(self) -> list[str]:
        """Return the names of all species entries in the AmP collection."""
        entries = self.list_directory(f"{self.base_url}/entries/", include_files=False)
        return [entry.rstrip("/") for entry in entries]

    def list_species_files(self, species: str, *, include_results_mat: bool = True) -> list[str]:
        """Return the estimation files available for ``species`` (result figures and html pages are excluded)."""
        files = self.list_directory(species_dir_url(species, self.base_url), include_dirs=False)
        files = [file for file in files if _is_species_estimation_file(file)]
        if not include_results_mat:
            files = [file for file in files if not file.startswith("results")]
        return files

    def download_species_file(
            self,
            species: str,
            file_name: str,
            dest_dir: str | os.PathLike,
            *,
            overwrite: bool = False,
            check_update: bool = False,
    ) -> DownloadStatus:
        return self.download_url(
            species_file_url(species, file_name, self.base_url),
            Path(dest_dir) / file_name,
            overwrite=overwrite,
            check_update=check_update,
        )

    def download_ampdata_file(
            self,
            file_name: str,
            dest_dir: str | os.PathLike,
            *,
            overwrite: bool = False,
            check_update: bool = False,
    ) -> DownloadStatus:
        return self.download_url(
            ampdata_file_url(file_name, self.base_url),
            Path(dest_dir) / file_name,
            overwrite=overwrite,
            check_update=check_update,
        )

    def download_url(
            self,
            url: str,
            save_path: str | os.PathLike,
            *,
            overwrite: bool = False,
            check_update: bool = False,
    ) -> DownloadStatus:
        """Download ``url`` to ``save_path``.

        Existing files are kept unless ``overwrite`` is set. With ``check_update``, a conditional GET
        (``If-Modified-Since`` the local modification time) replaces the local file only if the remote one is
        newer. Downloaded files take the remote ``Last-Modified`` time so later update checks stay accurate.
        Raises ``requests.RequestException`` on HTTP or connection errors; no partial file is left behind.
        """
        save_path = Path(save_path)
        exists = save_path.exists()
        headers = {}
        if exists and not overwrite:
            if not check_update:
                return DownloadStatus.SKIPPED_EXISTS
            headers["If-Modified-Since"] = formatdate(save_path.stat().st_mtime, usegmt=True)

        response_headers = self.fetch_to_file(url, save_path, headers=headers)
        if response_headers is None:
            return DownloadStatus.NOT_MODIFIED
        return DownloadStatus.UPDATED if exists else DownloadStatus.DOWNLOADED

    def fetch_to_file(
            self,
            url: str,
            save_path: str | os.PathLike,
            *,
            headers: dict[str, str] | None = None,
    ) -> Mapping[str, str] | None:
        """GET ``url`` into ``save_path`` and return the response headers, or None if the server answered 304.

        ``headers`` can carry conditional-request validators (``If-None-Match``, ``If-Modified-Since``).
        The file is written to a temporary ``.part`` file first, so a failed download never leaves a partial file
        and keeps any existing one. The saved file takes the remote ``Last-Modified`` time.
        Raises ``requests.RequestException`` on HTTP or connection errors.
        """
        save_path = Path(save_path)
        with self.session.get(url, headers=headers or {}, stream=True, timeout=self.timeout) as response:
            if response.status_code == 304:
                return None
            response.raise_for_status()

            save_path.parent.mkdir(parents=True, exist_ok=True)
            part_path = save_path.with_name(save_path.name + ".part")
            try:
                with open(part_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                os.replace(part_path, save_path)
            finally:
                if part_path.exists():
                    part_path.unlink()
            response_headers = response.headers

        last_modified = response_headers.get("Last-Modified")
        if last_modified:
            try:
                timestamp = parsedate_to_datetime(last_modified).timestamp()
                os.utime(save_path, (timestamp, timestamp))
            except (TypeError, ValueError):
                pass
        return response_headers
