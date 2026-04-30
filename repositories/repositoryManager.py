from __future__ import annotations

import json
from pathlib import Path


class RepositoryManager:
    def __init__(self, data_dir: Path | str | None = None):
        if data_dir is None:
            data_dir = Path(__file__).resolve().parent.parent / "data"
        self.data_dir = Path(data_dir)

    def _path(self, name: str) -> Path:
        return self.data_dir / f"{name}.json"

    def load(self, name: str) -> list | dict:
        path = self._path(name)
        if not path.exists():
            return []
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, name: str, data: list | dict) -> None:
        path = self._path(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def find_by_id(self, name: str, item_id: int) -> dict | None:
        items = self.load(name)
        if not isinstance(items, list):
            return None
        return next((i for i in items if i.get("id") == item_id), None)


repository_manager = RepositoryManager()
