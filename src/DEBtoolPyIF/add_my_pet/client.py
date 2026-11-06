"""HTTP client for listing and downloading files from the Add-my-Pet website."""

from __future__ import annotations

import os
import threading
import time
from email.utils import formatdate, parsedate_to_datetime
from enum import Enum
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .urls import AMP_BASE_URL, ampdata_file_url, species_dir_url, species_file_url

# Seconds between requests; the limit of the AmP server is not published
DEFAULT_REQUEST_DELAY = 0.5
# Seconds to connect and to read; a short connect timeout notices quickly that the server stopped responding
DEFAULT_TIMEOUT = (15.0, 60.0)


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
    Directory entries keep their trailing ``/``. Names are returned decoded (``my%20file.csv`` as ``my file.csv``).
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
        entries.append(unquote(href))
    return entries


def _is_species_estimation_file(file_name: str) -> bool:
    # Result figures are skipped, the results .mat file is kept
    return not file_name.startswith("results") or file_name.endswith(".mat")


class AmPClient:
    """Thin wrapper around a pooled ``requests.Session`` pointed at the AmP website.

    The same client can be shared between threads to download several species concurrently.

    The AmP server stops accepting connections after many requests, so requests are spaced ``request_delay`` seconds
    apart across all threads using this client.
    """

    def __init__(
            self,
            *,
            base_url: str = AMP_BASE_URL,
            timeout: float | tuple[float, float] = DEFAULT_TIMEOUT,
            max_retries: int = 2,
            pool_size: int = 50,
            request_delay: float = DEFAULT_REQUEST_DELAY,
            session: requests.Session | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.request_delay = request_delay
        self._pacing_lock = threading.Lock()
        self._next_request_time = 0.0
        if session is None:
            session = requests.Session()
            retry = Retry(total=max_retries, backoff_factor=2, status_forcelist=(429, 503), raise_on_status=False)
            adapter = HTTPAdapter(pool_connections=pool_size, pool_maxsize=pool_size, max_retries=retry)
            session.mount("https://", adapter)
            session.mount("http://", adapter)
        self.session = session

    def _wait_for_turn(self) -> None:
        if self.request_delay <= 0:
            return
        with self._pacing_lock:
            now = time.monotonic()
            request_time = max(now, self._next_request_time)
            self._next_request_time = request_time + self.request_delay
        if request_time > now:
            time.sleep(request_time - now)

    def list_directory(self, url: str, *, include_dirs: bool = True, include_files: bool = True) -> list[str]:
        self._wait_for_turn()
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return parse_directory_listing(response.text, include_dirs=include_dirs, include_files=include_files)

    def list_species(self) -> list[str]:
        """Return the names of all species entries in the AmP collection."""
        entries = self.list_directory(f"{self.base_url}/entries/", include_files=False)
        return [entry.rstrip("/") for entry in entries]

    def list_species_files(
            self,
            species: str,
            *,
            include_results_mat: bool = True,
            include_html: bool = True,
    ) -> list[str]:
        """Return the files in the ``species`` entry, excluding result figures.

        This includes data files that ``mydata`` or ``predict`` read (e.g. ``tL.txt``), which have no fixed names.
        """
        files = self.list_directory(species_dir_url(species, self.base_url), include_dirs=False)
        files = [file for file in files if _is_species_estimation_file(file)]
        if not include_results_mat:
            files = [file for file in files if not file.startswith("results")]
        if not include_html:
            files = [file for file in files if not file.lower().endswith(".html")]
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

        self._wait_for_turn()
        with self.session.get(url, headers=headers, stream=True, timeout=self.timeout) as response:
            if response.status_code == 304:
                return DownloadStatus.NOT_MODIFIED
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
            last_modified = response.headers.get("Last-Modified")

        if last_modified:
            try:
                timestamp = parsedate_to_datetime(last_modified).timestamp()
                os.utime(save_path, (timestamp, timestamp))
            except (TypeError, ValueError):
                pass
        return DownloadStatus.UPDATED if exists else DownloadStatus.DOWNLOADED
