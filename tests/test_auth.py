# [file name]: test_auth.py
import os
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from rnds.auth import Auth


class MockCacheHandler:
    """Implementação mock do protocolo de cache para testes."""

    def __init__(self):
        self.store = {}

    def get(self, key: str) -> str | None:
        return self.store.get(key)

    def set(self, key: str, value: str, seconds: int) -> None:
        self.store[key] = value


@pytest.fixture
def mock_cache_handler():
    """Fixture para mock do cache handler que implementa CacheProtocol."""
    return MockCacheHandler()


@pytest.fixture
def mock_async_client():
    """Fixture para mock do AsyncClient."""
    client = AsyncMock(spec=httpx.AsyncClient)
    client.get = AsyncMock()
    return client


@pytest.fixture
def auth_instance(mock_async_client, mock_cache_handler):
    """Fixture para instância de Auth com configurações padrão."""
    return Auth(
        client=mock_async_client,
        cache_handler=mock_cache_handler,
        auth_url="https://auth.example.com/",
        service_url="https://api.example.com",
    )


@pytest.mark.asyncio
async def test_auth_successful(auth_instance, mock_async_client):
    """Testa autenticação bem-sucedida e armazenamento no cache."""
    # Configura
    mock_response = MagicMock()
    mock_response.is_success = True
    mock_response.json.return_value = {
        "access_token": "test_token",
        "expires_in": 3600000,  # 1 hora em milissegundos
    }
    mock_async_client.get.return_value = mock_response

    # Executa
    await auth_instance.auth()

    # Verifica
    mock_async_client.get.assert_called_once_with("https://auth.example.com/token")
    assert auth_instance.cache.get("token_rnds") == "test_token"


@pytest.mark.asyncio
async def test_get_token_with_cached_token(auth_instance, mock_cache_handler):
    """Testa obtenção de token quando já existe no cache."""
    # Configura
    mock_cache_handler.set("token_rnds", "cached_token", 3600)

    # Executa
    result = await auth_instance.get_token()

    # Verifica
    assert result == "cached_token"
    auth_instance.client.get.assert_not_called()


@pytest.mark.asyncio
async def test_get_is_called(auth_instance, mock_cache_handler):
    """Testa obtenção de token quando já existe no cache."""
    # Configura
    mock_cache_handler.set("token_rnds", "cached_token", 3600)

    # Executa
    await auth_instance.get(url="https://api.example.com/resource")

    # Verifica
    auth_instance.client.get.assert_called()


@pytest.mark.asyncio
async def test_get_token_without_cached_token(auth_instance, mock_async_client):
    """Testa obtenção de token quando não existe no cache."""
    # Configura
    mock_response = MagicMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"access_token": "new_token", "expires_in": 3600000}
    mock_async_client.get.return_value = mock_response

    # Executa
    result = await auth_instance.get_token()

    # Verifica
    assert result == "new_token"
    mock_async_client.get.assert_called_once_with("https://auth.example.com/token")


@pytest.mark.asyncio
async def test_get_headers(auth_instance, mock_cache_handler):
    """Testa geração dos headers de autenticação."""
    # Configura
    mock_cache_handler.set("token_rnds", "test_token", 3600)
    os.environ["CNS_SEC_SAUDE"] = "cns_test"

    # Executa
    headers = await auth_instance.get_headers()

    # Verifica
    assert headers == {
        "Content-Type": "application/json",
        "X-Authorization-Server": "Bearer test_token",
        "Authorization": "cns_test",
    }


@pytest.mark.asyncio
async def test_auth_failure(auth_instance, mock_async_client):
    """Testa comportamento quando a autenticação falha."""
    # Configura
    mock_response = MagicMock()
    mock_response.is_success = False
    mock_response.status_code = 401
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        message="Auth failed", request=httpx.Request("GET", "https://auth.example.com/token"), response=mock_response
    )
    mock_async_client.get.return_value = mock_response

    # Executa e verifica
    with pytest.raises(httpx.HTTPStatusError):
        await auth_instance.auth()
    assert auth_instance.cache.get("token_rnds") is None


@pytest.mark.parametrize(
    "auth_url, service_url, expected_auth_url",
    [
        ("https://input.auth/", "https://input.api", "https://input.auth/token"),
        ("https://env.auth", "https://env.api", "https://env.auth/token"),
        ("", "", "/token"),
        ("https://input.auth/", "", "https://input.auth/token"),
    ],
    ids=["with_trailing_slash", "without_trailing_slash", "empty_urls", "only_auth_url"],
)
def test_url_initialization(auth_url, service_url, expected_auth_url, mock_async_client, mock_cache_handler):
    """Testa a construção correta das URLs."""
    auth = Auth(client=mock_async_client, cache_handler=mock_cache_handler, auth_url=auth_url, service_url=service_url)

    assert auth.auth_url == expected_auth_url
    assert auth.service_url == service_url


@pytest.mark.parametrize(
    "expires_in, expected_seconds",
    [
        (3600000, 3540),  # 1 hora - 10 minutos
        (600000, 0),  # 10 minutos - 10 minutos (não negativo)
        (300000, 0),  # 5 minutos - 10 minutos (limitado a 0)
    ],
    ids=["normal_case", "edge_case_10min", "edge_case_5min"],
)
@pytest.mark.asyncio
async def test_auth_expiration_calculation(expires_in, expected_seconds, auth_instance, mock_async_client):
    """Testa cálculo correto do tempo de expiração do token."""
    # Configura
    mock_response = MagicMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"access_token": "test_token", "expires_in": expires_in}
    mock_async_client.get.return_value = mock_response

    # Executa
    await auth_instance.auth()

    # Verifica
    assert auth_instance.cache.get("token_rnds") == "test_token"


@pytest.mark.asyncio
async def test_auth_with_missing_token_in_response(auth_instance, mock_async_client):
    """Testa comportamento quando a resposta não contém token."""
    # Configura
    mock_response = MagicMock()
    mock_response.is_success = True
    mock_response.json.return_value = {}  # Sem access_token
    mock_async_client.get.return_value = mock_response

    # Executa
    await auth_instance.auth()

    # Verifica
    assert auth_instance.cache.get("token_rnds") is None
