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
        client_id: str,
        client_secret: str,
        external_api_base_url: str,
        mecanismo: str
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
        self.client_id = client_id
        self.client_secret = client_secret
        self.external_api_base_url = external_api_base_url
        self.mecanismo = mecanismo

    async def auth(self) -> None:
        method = self.mecanismo.lower() or "api"
        if method == "basic":
            await self.basic_auth()

        elif method == "api":
            await self.external_api_auth()

    async def basic_auth(self) -> None:
        """Realiza autenticação na RNDS e armazena o token no cache."""
        response = await self.client.get(self.auth_url)
        response.raise_for_status()

        if response.is_success and response.json():
            access_token = response.json().get("access_token", None)
            expires_in_miliseconds = response.json().get("expires_in", None)
            seconds = int(expires_in_miliseconds / 1000) - 600
            self.cache.set("token_rnds", access_token, seconds)

    async def external_api_auth(self) -> None:
        """Realiza autenticação na RNDS utilizando uma API externa e armazena o token no cache."""
        client_id = self.client_id
        client_secret = self.client_secret
        external_api_base_url = self.external_api_base_url

        authorization_code_payload = {
            "username": client_id,
            "password": client_secret,
        }
        authorization_code_response = await self.client.post(
            f"{external_api_base_url}/login",
            json=authorization_code_payload,
        )
        authorization_code_response.raise_for_status()
        authorization_code = authorization_code_response.json().get("access_token", None)

        access_token_header = {"Authorization": f"Bearer {authorization_code}"}
        access_token_response = await self.client.post(
            f"{external_api_base_url}/token",
            headers=access_token_header,
        )
        access_token_response.raise_for_status()

        if access_token_response.is_success and access_token_response.json():
            access_token = access_token_response.json().get("access_token", None)
            if "Bearer" in access_token:
                access_token = access_token.split("Bearer ")[1]

            expires_in_miliseconds = access_token_response.json().get("expires_in", None)
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

    async def get(self, url: str) -> dict[str, str]:
        """Obtém os headers de autenticação para uma URL específica.

        Args:
            url (str): URL para a qual os headers serão gerados.

        Returns:
            dict[str, str]: Headers HTTP com autenticação.
        """
        return await self.client.get(url, headers=await self.get_headers())
