import json
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from rnds.auth import Auth
from rnds.rira import (
    ATTENDED_STATUS,
    BOOKED_STATUS,
    FULFILLED_STATUS,
    PENDING_STATUS,
    RETURNED_TO_REQUESTER_STATUS,
    RIRA,
    WAITLIST_STATUS,
    IdentificadorPacienteNaoInformado,
    RIRAException,
)


# Fixtures
@pytest.fixture
def mock_auth():
    auth = MagicMock(spec=Auth)
    auth.client = MagicMock()
    auth.get_headers = AsyncMock(return_value={"Authorization": "Bearer token"})
    return auth


@pytest.fixture
def rira_service(mock_auth):
    return RIRA(auth=mock_auth, service_url="http://test.com")


@pytest.fixture
def sample_bundle_data():
    return json.dumps({"resourceType": "Bundle", "type": "document"})


@pytest.fixture
def sample_patient_data():
    return {
        "id_paciente": "patient123",
        "id_solicitacao": "request456",
        "data_solicitacao": "2023-01-01",
        "cnes_solicitante": "cnes123",
        "codigo_sigtap": "sig123",
        "cid10": "A00",
    }


# Testes para inicialização
def test_rira_initialization_with_trailing_slash(mock_auth):
    service = RIRA(auth=mock_auth, service_url="http://test.com/")
    assert service.service_url == "http://test.com/"


def test_rira_initialization_without_trailing_slash(mock_auth):
    service = RIRA(auth=mock_auth, service_url="http://test.com")
    assert service.service_url == "http://test.com/"


def test_rira_initialization_bundle_id_system(mock_auth):
    with patch.dict(os.environ, {"BUND_ID_SYSTEM": "test_system"}):
        service = RIRA(auth=mock_auth, service_url="http://test.com")
        assert service.bundle_id_system == "test_system"


# Testes para submeter_documento_clinico
@pytest.mark.asyncio
async def test_submeter_documento_clinico_success(rira_service, mock_auth, sample_bundle_data):
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.headers = {"location": "http://test.com/fhir/r4/Bundle/123"}
    mock_response.text = "OK"
    mock_auth.client.post = AsyncMock(return_value=mock_response)

    doc_id = await rira_service.submeter_documento_clinico(sample_bundle_data)
    assert doc_id == "123"
    mock_auth.client.post.assert_called_once_with(
        "http://test.com/fhir/r4/Bundle", data=sample_bundle_data, headers={"Authorization": "Bearer token"}
    )


@pytest.mark.asyncio
async def test_submeter_documento_clinico_failure(rira_service, mock_auth, sample_bundle_data):
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    mock_auth.client.post = AsyncMock(return_value=mock_response)

    with pytest.raises(RIRAException) as excinfo:
        await rira_service.submeter_documento_clinico(sample_bundle_data)
    assert "Falha ao se comunicar com o rira. [400] Bad Request" in str(excinfo.value)


# Testes para obter_documento_clinico
@pytest.mark.asyncio
async def test_obter_documento_clinico_success(rira_service, mock_auth):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "Document content"
    mock_auth.client.get = AsyncMock(return_value=mock_response)

    result = await rira_service.obter_documento_clinico("doc123")
    assert result == mock_response
    mock_auth.client.get.assert_called_once_with(
        "http://test.com/fhir/r4/Composition/doc123", headers={"Authorization": "Bearer token"}
    )


@pytest.mark.asyncio
async def test_obter_documento_clinico_failure(rira_service, mock_auth):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"
    mock_auth.client.get = AsyncMock(return_value=mock_response)

    with pytest.raises(RIRAException) as excinfo:
        await rira_service.obter_documento_clinico("doc123")
    assert "Falha ao se comunicar com o rira. [404] Not Found" in str(excinfo.value)


# Testes para criar_documento_pending
def test_criar_documento_pending(rira_service, sample_patient_data):
    document = rira_service.criar_documento_pending(**sample_patient_data)

    assert document is not None
    assert isinstance(document, dict)
    assert "resourceType" in document
    assert document["resourceType"] == "Bundle"
    assert "entry" in document
    assert len(document["entry"]) == 4  # 4 recursos no bundle


# Testes para criar_documento_returned_to_requester
def test_criar_documento_returned_to_requester(rira_service, sample_patient_data):
    document = rira_service.criar_documento_returned_to_requester(cnes_regulador="cnes_reg456", **sample_patient_data)

    assert document is not None
    assert isinstance(document, dict)
    assert "resourceType" in document
    assert document["resourceType"] == "Bundle"


# Testes para criar_documento_booked
def test_criar_documento_booked(rira_service, sample_patient_data):
    document = rira_service.criar_documento_booked(
        cnes_regulador="cnes_reg456",
        cnes_executante="cnes_exec789",
        data_autorizacao="2023-01-02",
        cbo="cbo123",
        **sample_patient_data,
    )

    assert document is not None
    assert isinstance(document, dict)
    assert "resourceType" in document
    assert document["resourceType"] == "Bundle"


# Testes para criar_documento_attended
def test_criar_documento_attended(rira_service, sample_patient_data):
    document = rira_service.criar_documento_attended(
        cnes_regulador="cnes_reg456",
        cnes_executante="cnes_exec789",
        data_autorizacao="2023-01-02",
        data_execucao="2023-01-03",
        cbo="cbo123",
        **sample_patient_data,
    )

    assert document is not None
    assert isinstance(document, dict)
    assert "resourceType" in document
    assert document["resourceType"] == "Bundle"


# Testes para criar_documento (método principal)
def test_criar_documento_minimal(rira_service, sample_patient_data):
    document = rira_service.criar_documento(
        status_composition=PENDING_STATUS, status_appointment=WAITLIST_STATUS, **sample_patient_data
    )

    assert document is not None
    assert isinstance(document, dict)
    assert "resourceType" in document
    assert document["resourceType"] == "Bundle"


def test_criar_documento_with_optional_params(rira_service, sample_patient_data):
    document = rira_service.criar_documento(
        status_composition=BOOKED_STATUS,
        status_appointment=BOOKED_STATUS,
        cnes_regulador="cnes_reg456",
        cnes_executante="cnes_exec789",
        data_autorizacao="2023-01-02",
        data_execucao="2023-01-03",
        cbo="cbo123",
        relates_to="related_doc123",
        **sample_patient_data,
    )

    assert document is not None
    assert isinstance(document, dict)
    assert "resourceType" in document
    assert document["resourceType"] == "Bundle"


# Testes para comportamento com dados inválidos
def test_criar_documento_missing_patient_id(rira_service, sample_patient_data):
    with pytest.raises(IdentificadorPacienteNaoInformado):
        invalid_data = sample_patient_data.copy()
        invalid_data["id_paciente"] = ""
        rira_service.criar_documento(
            status_composition=PENDING_STATUS, status_appointment=WAITLIST_STATUS, **invalid_data
        )


# Testes para constantes
def test_constants():
    assert PENDING_STATUS == "pending"
    assert RETURNED_TO_REQUESTER_STATUS == "returned-to-requester"
    assert WAITLIST_STATUS == "waitlist"
    assert BOOKED_STATUS == "booked"
    assert ATTENDED_STATUS == "attended"
    assert FULFILLED_STATUS == "fulfilled"


# Testes para exceções
def test_exceptions():
    assert issubclass(IdentificadorPacienteNaoInformado, BaseException)
    assert issubclass(RIRAException, Exception)
