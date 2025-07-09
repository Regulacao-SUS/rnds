import pytest
from unittest.mock import AsyncMock
from rnds.cfm import CFMClient
from zeep import exceptions


@pytest.fixture
def mock_zeep_client():
    """Fixture para mock do AsyncClient do zeep."""
    return AsyncMock()


@pytest.fixture
def cfm_client(mock_zeep_client):
    """Fixture para CFMClient com mocks configurados."""
    return CFMClient(client=mock_zeep_client, chave="fake-key")


@pytest.mark.asyncio
async def test_validar_success(cfm_client):
    """Testa validação bem-sucedida de médico."""
    # Configura
    mock_service = AsyncMock()
    cfm_client.client.service = mock_service
    mock_service.Validar.return_value = {"nome": "Dr. Teste", "crm": "1234567"}

    # Executa
    result = await cfm_client.validar(1234567, "SP", "12345678901", "01/01/1980")

    # Verifica
    assert result == {"nome": "Dr. Teste", "crm": "1234567"}
    mock_service.Validar.assert_awaited_once_with(1234567, "SP", "12345678901", "01/01/1980", "fake-key")


@pytest.mark.asyncio
async def test_validar_fault_exception(cfm_client):
    """Testa validação que retorna Fault exception."""
    # Configura
    mock_service = AsyncMock()
    cfm_client.client.service = mock_service
    mock_service.Validar.side_effect = exceptions.Fault("Erro no serviço")

    # Executa
    result = await cfm_client.validar(1234567, "SP", "12345678901", "01/01/1980")

    # Verifica
    assert result is False
    mock_service.Validar.assert_awaited_once_with(1234567, "SP", "12345678901", "01/01/1980", "fake-key")


@pytest.mark.parametrize(
    "crm, uf, cpf, datanasc, expected_key",
    [
        (1234567, "SP", "12345678901", "01/01/1980", "fake-key"),  # Caso normal
        (7654321, "RJ", "98765432109", "31/12/1975", "fake-key"),  # Outros valores
    ],
)
@pytest.mark.asyncio
async def test_validar_with_different_inputs(cfm_client, crm, uf, cpf, datanasc, expected_key):
    """Testa validação com diferentes entradas (table-driven test)."""
    # Configura
    mock_service = AsyncMock()
    cfm_client.client.service = mock_service
    mock_service.Validar.return_value = {"nome": "Dr. Teste", "crm": str(crm)}

    # Executa
    result = await cfm_client.validar(crm, uf, cpf, datanasc)

    # Verifica
    assert result == {"nome": "Dr. Teste", "crm": str(crm)}
    mock_service.Validar.assert_awaited_once_with(crm, uf, cpf, datanasc, expected_key)


@pytest.mark.asyncio
async def test_consulta_simples_success(cfm_client):
    """Testa consulta simples bem-sucedida."""
    # Configura
    mock_service = AsyncMock()
    cfm_client.client.service = mock_service
    mock_service.Consultar.return_value = {"nome": "Dr. Simples", "crm": "7654321"}

    # Executa
    result = await cfm_client.consulta_simples(7654321, "RJ")

    # Verifica
    assert result == {"nome": "Dr. Simples", "crm": "7654321"}
    mock_service.Consultar.assert_awaited_once_with(7654321, "RJ", "fake-key")


@pytest.mark.asyncio
async def test_consulta_completa_success(cfm_client):
    """Testa consulta completa bem-sucedida."""
    # Configura
    mock_service = AsyncMock()
    cfm_client.client.service = mock_service
    mock_service.ConsultaCompleta.return_value = {
        "nome": "Dr. Completo",
        "crm": "1112223",
        "especialidades": ["Cardiologia", "Clínica Médica"],
    }

    # Executa
    result = await cfm_client.consulta_completa(1112223, "MG", "11122233344", "15/05/1972")

    # Verifica
    assert result == {"nome": "Dr. Completo", "crm": "1112223", "especialidades": ["Cardiologia", "Clínica Médica"]}
    mock_service.ConsultaCompleta.assert_awaited_once_with(1112223, "MG", "11122233344", "15/05/1972", "fake-key")


@pytest.mark.asyncio
async def test_consulta_simples_with_zeep_fault(cfm_client):
    """Testa comportamento quando zeep lança Fault em consulta_simples."""
    # Configura
    mock_service = AsyncMock()
    cfm_client.client.service = mock_service
    mock_service.Consultar.side_effect = exceptions.Fault("Erro no serviço")

    # Executa e verifica exceção
    with pytest.raises(exceptions.Fault):
        await cfm_client.consulta_simples(1234567, "SP")


@pytest.mark.asyncio
async def test_consulta_completa_with_zeep_fault(cfm_client):
    """Testa comportamento quando zeep lança Fault em consulta_completa."""
    # Configura
    mock_service = AsyncMock()
    cfm_client.client.service = mock_service
    mock_service.ConsultaCompleta.side_effect = exceptions.Fault("Erro no serviço")

    # Executa e verifica exceção
    with pytest.raises(exceptions.Fault):
        await cfm_client.consulta_completa(1234567, "SP", "12345678901", "01/01/1980")
