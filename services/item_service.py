from __future__ import annotations

from repositories.repositoryManager import repository_manager

ITEMS_KEY = "items"


def get_all_items() -> list[dict]:
    items = repository_manager.load(ITEMS_KEY)
    return items if isinstance(items, list) else []


def get_item(item_id: int) -> dict | None:
    return repository_manager.find_by_id(ITEMS_KEY, item_id)
