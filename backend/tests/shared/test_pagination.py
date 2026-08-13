import pytest

from app.shared.database.pagination import Page, PaginationParams


def test_pagination_params_calculates_offset() -> None:
    pagination = PaginationParams(page=3, page_size=10)

    assert pagination.offset == 20


@pytest.mark.parametrize("page,page_size", [(0, 10), (1, 0), (1, 101)])
def test_pagination_params_rejects_invalid_values(page: int, page_size: int) -> None:
    with pytest.raises(ValueError):
        PaginationParams(page=page, page_size=page_size)


def test_page_calculates_total_pages() -> None:
    page = Page(items=["record"], total=21, page=1, page_size=10)

    assert page.total_pages == 3
