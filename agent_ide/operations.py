"""Available text operations."""

def uppercase(text: str, **_: str) -> str:
    """Convert text to uppercase."""
    return text.upper()


def prefix(text: str, value: str = "") -> str:
    """Prefix text with ``value``."""
    return f"{value}{text}"
