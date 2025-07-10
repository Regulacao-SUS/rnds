# test_rira.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from rnds.auth import Auth
from rnds.rira_resources.bundle import Bundle
from rnds.rira import RIRA


@pytest.fixture
def mock_auth():
    auth = MagicMock(spec=Auth)
    auth.get_token = AsyncMock(return_value="fake_token")
    auth.get_headers = AsyncMock(return_value={"Authorization": "Bearer fake_token"})
    auth.client = MagicMock()
    auth.client.post = AsyncMock()
    return auth


@pytest.fixture
def mock_bundle():
    return MagicMock(spec=Bundle)


@pytest.fixture
def rira_service(mock_auth):
    return RIRA(auth=mock_auth, service_url="https://api.example.com/", bundle_uri="fhir/r4/Bundle")


@pytest.mark.asyncio
async def test_rira_initialization_requires_all_parameters():
    """Testa que a inicialização da classe RIRA requer todos os parâmetros."""
    auth = MagicMock(spec=Auth)

    # Testa com todos os parâmetros
    rira = RIRA(auth=auth, service_url="https://api.example.com/", bundle_uri="fhir/r4/Bundle")

    assert rira.service_url == "https://api.example.com/"
    assert rira.bundle_uri == "fhir/r4/Bundle"
    assert rira.auth == auth

    # Testa que falta de parâmetros gera TypeError
    with pytest.raises(TypeError):
        RIRA(auth=auth, service_url="https://api.example.com/")

    with pytest.raises(TypeError):
        RIRA(auth=auth, bundle_uri="fhir/r4/Bundle")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "service_url, bundle_uri",
    [
        ("https://api1.example.com/", "fhir/r4/Bundle1"),
        ("https://api2.example.com/", "fhir/r4/Bundle2"),
        ("https://api3.example.com/v2/", "custom/path"),
    ],
    ids=["api1", "api2", "custom_path"],
)
async def test_rira_initialization_with_different_urls(service_url, bundle_uri, mock_auth):
    """Testa a inicialização com diferentes URLs (table driven test)."""
    rira = RIRA(auth=mock_auth, service_url=service_url, bundle_uri=bundle_uri)

    assert rira.service_url == service_url
    assert rira.bundle_uri == bundle_uri


@pytest.mark.asyncio
@pytest.mark.parametrize("token_value", ["token_123", "another_token", "yet_another_token"])
async def test_test_token_method(token_value, mock_auth):
    """Testa o método test_token com diferentes valores de token (table driven test)."""
    mock_auth.get_token.return_value = token_value

    rira = RIRA(auth=mock_auth, service_url="https://api.example.com/", bundle_uri="fhir/r4/Bundle")

    result = await rira.test_token()

    assert result == token_value
    mock_auth.get_token.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "bundle_data,expected_url",
    [
        ('{"resourceType": "Bundle"}', "https://api.example.com/fhir/r4/Bundle"),
        ('{"resourceType": "Bundle", "id": "123"}', "https://api.example.com/fhir/r4/Bundle"),
        ('{"resourceType": "Bundle", "type": "document"}', "https://api.example.com/fhir/r4/Bundle"),
    ],
    ids=["simple_bundle", "bundle_with_id", "bundle_with_type"],
)
async def test_post_documento_clinico(bundle_data, expected_url, rira_service, mock_auth):
    """Testa o método post_documento_clinico com diferentes bundles (table driven test)."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_auth.client.post.return_value = mock_response

    result = await rira_service.post_documento_clinico(bundle_data)

    mock_auth.client.post.assert_called_once_with(
        expected_url, data=bundle_data, headers={"Authorization": "Bearer fake_token"}
    )
    assert result == mock_response


@pytest.mark.asyncio
async def test_post_documento_clinico_behavior(rira_service, mock_auth):
    """Testa o comportamento do método post_documento_clinico (BDD style)."""
    # Given
    bundle_data = '{"resourceType": "Bundle", "id": "test-123"}'
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_auth.client.post.return_value = mock_response

    # When
    result = await rira_service.post_documento_clinico(bundle_data)

    # Then
    mock_auth.get_headers.assert_called_once()
    mock_auth.client.post.assert_called_once_with(
        "https://api.example.com/fhir/r4/Bundle", data=bundle_data, headers={"Authorization": "Bearer fake_token"}
    )
    assert result == mock_response
    assert result.status_code == 201


@pytest.mark.asyncio
async def test_post_documento_clinico_error_handling(rira_service, mock_auth):
    """Testa o tratamento de erros no método post_documento_clinico."""
    # Given - Simula um erro na requisição
    mock_auth.client.post.side_effect = Exception("Connection error")

    # When/Then - Verifica que a exceção é propagada
    with pytest.raises(Exception, match="Connection error"):
        await rira_service.post_documento_clinico('{"resourceType": "Bundle"}')
