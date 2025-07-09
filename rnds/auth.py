import os
from typing import Protocol

from httpx import AsyncClient

from rnds.base_auth import BaseAuth


class CacheProtocol(Protocol):
    """Protocolo para o handler de cache utilizado pelo serviço de autenticação."""

    def get(self, key: str) -> str | None:
        """Obtém um valor do cache."""

    def set(self, key: str, value: str, seconds: int) -> None:
        """Define um valor no cache com expiração em segundos."""


class Auth(BaseAuth):
    """Serviço de autenticação para integração com a RNDS.

    Gerencia autenticação, obtenção e cache de tokens de acesso para a RNDS.
    """

    __slots__ = ("auth_url", "service_url", "client", "cert_filepath", "key_filepath")

    def __init__(
        self,
        client: AsyncClient,
        cache_handler: CacheProtocol,
        auth_url: str,
        service_url: str,
    ) -> None:
        """Inicializa o serviço de autenticação RNDS.

        Args:
            cache_handler (object): Handler para cache de tokens.
            auth_url (str, opcional): URL base de autenticação da RNDS.
            service_url (str, opcional): URL base da API da RNDS.
            cert_filepath (str, opcional): Caminho para o certificado do cliente.
            key_filepath (str, opcional): Caminho para a chave privada do cliente.
        """
        self.cache = cache_handler
        self.auth_url = auth_url.rstrip("/") + "/token"
        self.service_url = service_url
        self.client = client

    async def auth(self) -> None:
        """Realiza autenticação na RNDS e armazena o token no cache."""
        response = await self.client.get(self.auth_url)
        response.raise_for_status()

        if response.is_success and response.json():
            access_token = response.json().get("access_token", None)
            expires_in_miliseconds = response.json().get("expires_in", None)
            seconds = int(expires_in_miliseconds / 1000) - 600
            self.cache.set("token_rnds", access_token, seconds)

    async def get_token(self) -> str:
        """Obtém o token de acesso da RNDS, autenticando se necessário.

        Returns:
            str: Token de acesso válido.
        """
        if self.cache.get("token_rnds"):
            return self.cache.get("token_rnds")
        await self.auth()
        return self.cache.get("token_rnds")

    async def get_headers(self) -> dict[str, str]:
        """Gera os headers de autenticação para requisições à RNDS.

        Returns:
            dict[str, str]: Headers HTTP com autenticação.
        """
        token = await self.get_token()

        headers = {
            "Content-Type": "application/json",
            "X-Authorization-Server": f"Bearer {token}",
            "Authorization": os.environ.get("CNS_SEC_SAUDE", ""),
        }
        return headers
