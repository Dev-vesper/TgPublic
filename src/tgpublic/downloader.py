import logging
import re
from pathlib import Path

import requests

from tgpublic.config import CHUNK_SIZE, USER_AGENT

logger = logging.getLogger("tgpublic")

MAX_FILENAME_LENGTH = 200


class FileDownloader:
    def __init__(self) -> None:
        self.headers = {"User-Agent": USER_AGENT}

    def download(self, url: str, output_dir: str, filename: str | None = None) -> Path | None:
        try:
            response = requests.get(
                url,
                headers=self.headers,
                stream=True,
                timeout=30,
                allow_redirects=True,
            )
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error("Download request failed for %s: %s", url, e)
            return None

        resolved_filename = self._resolve_filename(response, filename)
        resolved_filename = self._truncate_filename(resolved_filename)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        local_path = self._unique_path(output_path / resolved_filename)

        try:
            with open(local_path, "wb") as file_handle:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:
                        file_handle.write(chunk)
        except OSError as e:
            logger.error("Failed writing file %s: %s", local_path, e)
            return None

        return local_path

    def _resolve_filename(self, response, fallback_filename):
        content_disposition = response.headers.get("content-disposition")
        if content_disposition:
            match = re.search(r'filename[^;=\n]*=(["\']?)(.*?)\1', content_disposition)
            if match:
                return re.sub(r'[<>:"/\\|?*]', "_", match.group(2))

        if fallback_filename:
            return re.sub(r'[<>:"/\\|?*]', "_", fallback_filename)

        parsed = urllib.parse.urlparse(response.url)
        return Path(parsed.path).name or "downloaded_file.bin"

    def _truncate_filename(self, filename: str) -> str:
        if len(filename) <= MAX_FILENAME_LENGTH:
            return filename

        base, ext = Path(filename).stem, Path(filename).suffix
        ext = ext[:20]  # guard against abnormally long extensions
        keep = MAX_FILENAME_LENGTH - len(ext)
        return base[:keep] + ext

    def _unique_path(self, path: Path) -> Path:
        if not path.exists():
            return path
        stem = path.stem
        suffix = path.suffix
        parent = path.parent
        counter = 1
        while True:
            new_path = parent / f"{stem}_{counter}{suffix}"
            if not new_path.exists():
                return new_path
            counter += 1