from abc import ABC, abstractmethod


class BaseAuth(ABC):
    """Classe base abstrata para serviços de autenticação."""

    @abstractmethod
    async def auth(self) -> None:
        """Realiza autenticação e armazena o token de acesso."""

    @abstractmethod
    async def get_token(self) -> str:
        """Obtém o token de acesso autenticado.

        Returns:
            str: Token de acesso válido.
        """

    @abstractmethod
    async def get_headers(self) -> dict[str, str]:
        """Gera os headers de autenticação para requisições.

        Returns:
            dict[str, str]: Headers HTTP com autenticação.
        """
