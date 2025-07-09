from datetime import datetime


def stringify_data(data: datetime) -> str:
    """Converte um objeto datetime para string no formato ISO-8601 com timezone -03:00.

    Args:
        data (datetime): Data a ser convertida.

    Returns:
        str: Data formatada.
    """
    return data.isoformat(timespec="seconds") + "-03:00"
