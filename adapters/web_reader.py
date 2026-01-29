"""
Web Reader Adapter using Trafilatura.

Trafilatura combines fetching and extraction:
https://trafilatura.readthedocs.io/
"""

from typing import Dict

from trafilatura import extract, fetch_url
from trafilatura.metadata import extract_metadata


class WebReaderAdapter:
    """Adapter for reading web page content using Trafilatura."""

    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout

    def read(self, url: str) -> Dict:
        """
        Fetch and extract main content from a URL.

        Returns dict with: success, content, title, error
        """
        try:
            downloaded = fetch_url(url)

            if not downloaded:
                return {
                    "success": False,
                    "error": "Failed to download page",
                    "content": None,
                    "title": None,
                }

            content = extract(
                downloaded,
                include_comments=False,
                include_tables=True,
                no_fallback=False,
            )

            if not content:
                return {
                    "success": False,
                    "error": "Could not extract content from page",
                    "content": None,
                    "title": None,
                }

            metadata = extract_metadata(downloaded)
            title = metadata.title if metadata else None

            return {"success": True, "content": content, "title": title, "error": None}

        except Exception as e:
            return {"success": False, "error": str(e), "content": None, "title": None}
