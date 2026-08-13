"""Framework-independent pagination contracts."""

from collections.abc import Sequence
from dataclasses import dataclass
from math import ceil
from typing import TypeVar

ItemT = TypeVar("ItemT")


@dataclass(frozen=True, slots=True)
class PaginationParams:
    """Validated offset-pagination input independent of HTTP transport."""

    page: int = 1
    page_size: int = 25
    max_page_size: int = 100

    def __post_init__(self) -> None:
        if self.page < 1:
            raise ValueError("page must be at least 1")
        if not 1 <= self.page_size <= self.max_page_size:
            raise ValueError(f"page_size must be between 1 and {self.max_page_size}")

    @property
    def offset(self) -> int:
        """Return the number of rows to skip."""
        return (self.page - 1) * self.page_size


@dataclass(frozen=True, slots=True)
class Page[ItemT]:
    """A page of results plus enough metadata for client navigation."""

    items: Sequence[ItemT]
    total: int
    page: int
    page_size: int

    @property
    def total_pages(self) -> int:
        """Return the total number of pages, including an empty result set as zero."""
        return ceil(self.total / self.page_size) if self.total else 0
