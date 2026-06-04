from datetime import datetime


def get_current_year() -> int:
    return datetime.now().year


def normalize_isbn(isbn: str) -> str:
    """Strip dashes and spaces: '978-0-13-235088-4' → '9780132350884'."""
    return isbn.replace("-", "").replace(" ", "")


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix
