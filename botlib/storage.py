import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict

DEFAULT_DATA = {"products": {}, "pending": [], "languages": {}}


class JSONStorage:
    """Simple JSON file storage with an async lock."""

    def __init__(self, path: Path):
        self.path = path
        self.lock = asyncio.Lock()

    async def load(self) -> Dict[str, Any]:
        """Load data from the JSON file, returning defaults on error."""
        async with self.lock:
            try:
                with open(self.path, "r") as fh:
                    return json.load(fh)
            except FileNotFoundError:
                return DEFAULT_DATA.copy()
            except (OSError, json.JSONDecodeError) as exc:
                logging.error("Failed to load %s: %s", self.path, exc)
                return DEFAULT_DATA.copy()

    async def save(self, data: Dict[str, Any]) -> None:
        """Write *data* atomically to the JSON file."""
        async with self.lock:
            tmp = self.path.with_suffix(".tmp")
            try:
                with open(tmp, "w") as fh:
                    json.dump(data, fh, indent=2)
                os.replace(tmp, self.path)
            except OSError as exc:
                logging.error("Failed to save %s: %s", self.path, exc)
                # Cleanup temp file on error
                try:
                    tmp.unlink(missing_ok=True)
                except Exception:  # pragma: no cover - best effort cleanup
                    pass
