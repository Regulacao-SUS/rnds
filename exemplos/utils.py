from datetime import datetime


def stringify_data(data: datetime) -> str:
    """Converte um objeto datetime para string no formato ISO-8601 com timezone -03:00.

    Args:
        data (datetime): Data a ser convertida.

    Returns:
        str: Data formatada.
    """
    return data.isoformat(timespec="seconds") + "-03:00"


class DummyCacheHandler:
    """Classe dummy para simular o cache de tokens."""

    def __init__(self):
        self.cache = {}

    def get(self, key: str) -> str | None:
        return self.cache.get(key)

    def set(self, key: str, value: str, seconds: int) -> None:
        self.cache[key] = value
