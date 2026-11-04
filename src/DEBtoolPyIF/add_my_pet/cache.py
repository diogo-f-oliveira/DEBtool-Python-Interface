"""Local cache for files fetched from the Add-my-Pet website.

Each cached file has a JSON sidecar (``<file>.amp.json``) recording where it came from, the server's ``ETag`` and
``Last-Modified`` validators, and a SHA-256 hash of the downloaded content. The validators make update checks
exact (the server compares versions, not clocks) and the hash detects cached files that were edited locally.
"""

from __future__ import annotations

import hashlib
import json
import os
import warnings
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from email.utils import formatdate
from pathlib import Path
from typing import Iterable

import platformdirs
import requests

from .client import AmPClient

CACHE_DIR_ENV_VAR = "DEBTOOLPYIF_AMP_CACHE"
METADATA_SUFFIX = ".amp.json"


@dataclass(frozen=True)
class CacheRecord:
    """Contents of the sidecar file stored next to each cached file."""

    url: str
    etag: str | None
    last_modified: str | None
    sha256: str
    fetched_at: str


def get_cache_dir(cache_dir: str | os.PathLike | None = None) -> Path:
    """Return the folder where fetched AmP files are cached.

    In order of precedence: ``cache_dir`` if given, the ``DEBTOOLPYIF_AMP_CACHE`` environment variable, or the
    operating system's user cache folder (e.g. ``%LOCALAPPDATA%\\DEBtoolPyIF\\Cache\\add_my_pet`` on Windows,
    ``~/.cache/DEBtoolPyIF/add_my_pet`` on Linux, ``~/Library/Caches/DEBtoolPyIF/add_my_pet`` on macOS).
    """
    if cache_dir is not None:
        return Path(cache_dir)
    env_dir = os.environ.get(CACHE_DIR_ENV_VAR)
    if env_dir:
        return Path(env_dir)
    return Path(platformdirs.user_cache_dir("DEBtoolPyIF", appauthor=False)) / "add_my_pet"


def _metadata_path(path: Path) -> Path:
    return path.with_name(path.name + METADATA_SUFFIX)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as file:
        for chunk in iter(lambda: file.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_cache_record(path: str | os.PathLike) -> CacheRecord | None:
    """Return the sidecar record of a cached file, or None if the file is not managed by the cache."""
    metadata_path = _metadata_path(Path(path))
    try:
        return CacheRecord(**json.loads(metadata_path.read_text(encoding="utf-8")))
    except (OSError, ValueError, TypeError):
        return None


def _write_cache_record(path: Path, record: CacheRecord) -> None:
    _metadata_path(path).write_text(json.dumps(asdict(record), indent=2), encoding="utf-8")


def fetch_cached_file(client: AmPClient, url: str, path: str | os.PathLike, *, check_update: bool) -> Path:
    """Make sure ``path`` holds a copy of ``url`` and return it.

    - Not cached, or cached but edited locally (hash mismatch): download it.
    - Cached and ``check_update`` is False: use it without contacting the server.
    - Cached and ``check_update`` is True: conditional GET with the stored ``ETag``/``Last-Modified``; the file is
      only transferred if the server has a different version.
    If the server cannot be reached and a cached copy exists, the cached copy is used with a warning.
    """
    path = Path(path)
    record = read_cache_record(path)
    cached = path.exists()
    if cached and record is not None and _sha256(path) != record.sha256:
        warnings.warn(f"Cached file {path} was modified after download; downloading it again.")
        cached = False

    if cached and not check_update:
        return path

    headers = {}
    if cached:
        if record is None:
            # File placed in the cache by other means; fall back to its modification time
            headers["If-Modified-Since"] = formatdate(path.stat().st_mtime, usegmt=True)
        else:
            if record.etag:
                headers["If-None-Match"] = record.etag
            if record.last_modified:
                headers["If-Modified-Since"] = record.last_modified

    try:
        response_headers = client.fetch_to_file(url, path, headers=headers)
    except requests.RequestException as error:
        if not path.exists():
            raise
        warnings.warn(f"Could not reach AmP to fetch {path.name} ({error}); using the cached copy.")
        return path

    if response_headers is not None:
        _write_cache_record(path, CacheRecord(
            url=url,
            etag=response_headers.get("ETag"),
            last_modified=response_headers.get("Last-Modified"),
            sha256=_sha256(path),
            fetched_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        ))
    return path


def clear_cache(species: str | Iterable[str] | None = None, *, cache_dir: str | os.PathLike | None = None) -> list[Path]:
    """Delete cached AmP files and return the paths of the deleted files.

    @param species: species whose cached files are deleted. If None, the whole cache is cleared (including
        ``allStat.mat``).
    @param cache_dir: cache folder, see ``get_cache_dir``.
    Only files written by the cache (those with a ``.amp.json`` sidecar) are deleted, so pointing ``cache_dir`` at
    a folder with other files never removes them.
    """
    root = get_cache_dir(cache_dir)
    if species is None:
        folders = [root]
    else:
        folders = [root / species] if isinstance(species, str) else [root / name for name in species]

    removed = []
    for folder in folders:
        if not folder.is_dir():
            continue
        for metadata_path in sorted(folder.rglob(f"*{METADATA_SUFFIX}")):
            data_path = metadata_path.with_name(metadata_path.name[:-len(METADATA_SUFFIX)])
            if data_path.exists():
                data_path.unlink()
                removed.append(data_path)
            metadata_path.unlink()
        # Remove folders left empty, deepest first
        for directory in sorted((d for d in folder.rglob("*") if d.is_dir()), key=lambda d: len(d.parts), reverse=True):
            if not any(directory.iterdir()):
                directory.rmdir()
        if folder != root and not any(folder.iterdir()):
            folder.rmdir()
    return removed
