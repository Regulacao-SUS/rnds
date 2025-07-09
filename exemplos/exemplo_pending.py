import json
import os
from datetime import datetime, timedelta

from httpx import AsyncClient, Response

from exemplos.utils import stringify_data
from rnds.auth import Auth
from rnds.rira.appointment import Appointment
from rnds.rira.bundle import Bundle
from rnds.rira.composition import Composition
from rnds.rira.condition import Condition
from rnds.rira.rira import RIRA
from rnds.rira.service_request import ServiceRequest


class DummyCacheHandler:
    """Classe dummy para simular o cache de tokens."""

    def __init__(self):
        self.cache = {}

    def get(self, key: str) -> str | None:
        return self.cache.get(key)

    def set(self, key: str, value: str, seconds: int) -> None:
        self.cache[key] = value


class DummyHttpxClient(AsyncClient):
    """Classe dummy para simular o cliente httpx."""

    def __init__(self):
        super().__init__()
        self.is_success = True
        self.json_data = {}

    async def post(self, url: str, data: str, headers: dict) -> Response:
        """Simula uma requisição POST."""
        return Response(
            status_code=201,
            json=self.json_data,
            headers=headers,
            request=self.build_request("POST", url, data=data, headers=headers),
        )

    def json(self):
        """Retorna os dados JSON simulados."""
        return self.json_data


async def exemplo_pending() -> None:
    """Exemplo de criação de bundle com status pending para testes de integração RNDS."""
    httpx_async_client = AsyncClient(cert=(os.getenv("CERT_FILEPATH"), os.getenv("KEY_FILEPATH")), verify=True)
    auth = Auth(
        DummyCacheHandler(), httpx_async_client, os.environ.get("RNDS_AUTH_URL", ""), os.environ.get("RNDS_API_URL", "")
    )
    bundle = Bundle(
        "c1256970-5464-403d-99f9-f1ef1d1f81ea",
        id_system=os.environ.get("BUND_ID_SYSTEM", ""),
    )
    data_agora = datetime.now()
    data_autorizacao = data_agora + timedelta(hours=24)
    data_autorizacao = stringify_data(data_autorizacao)
    bundle_timestamp = stringify_data(data_agora)

    id_regulacao_assistencial = "urn:uuid:transient-0"
    id_agendamento = "urn:uuid:transient-1"
    id_requisicao = "urn:uuid:transient-2"
    id_cid10 = "urn:uuid:transient-3"

    cid10 = Condition(
        cond_clinical_status_code="active",
        cond_category_code="01",
        cond_category_display="Principal",
        cond_code_code="K922",
        cond_subject_id="708108612093340",
        cond_note_text="Sem observa\u00e7\u00f5es",
    ).gerar_dict()

    requisicao = ServiceRequest(
        sr_status="active",
        sr_intent="proposal",
        sr_category_code="04",
        sr_priority="routine",
        sr_code_code="0209010029",
        sr_subject_id="708108612093340",
        sr_requester_id="6994547",
        sr_performer_type_code="225225",
        sr_performer_id="0440620",
        sr_authored_on=bundle_timestamp,
    ).gerar_dict(id_cid10)

    agendamento = Appointment(
        app_status="booked",
        app_service_category_code="04",
        app_service_type_code="0209010029",
        app_specialty_code="225225",
        app_type_code="routine",
        app_participant_type_code="PCT",
        app_participant_status="accepted",
        app_patient_id="708108612093340",
        app_created_time=data_autorizacao,
        app_start_time=data_autorizacao,
        app_end_time=data_autorizacao,
    ).gerar_dict(id_requisicao, id_cid10)

    regulacao_assistencial = Composition(
        comp_status="final",
        comp_type_code="RA",
        comp_category_code="04",
        comp_subject_id="10165786442",
        comp_author_id="6450091",
        comp_title="Registro de Informações da Regulação Assistencial",
        comp_event_code="pending",
        comp_event_performer_id="6689477",
    ).gerar_dict(id_requisicao, id_agendamento, bundle_timestamp)

    recursos = {
        id_regulacao_assistencial: regulacao_assistencial,
        id_agendamento: agendamento,
        id_requisicao: requisicao,
        id_cid10: cid10,
    }
    bundle_data = bundle.montar_pacote_json(recursos, bundle_timestamp)

    rira_service = RIRA(
        auth=auth,
        bundle=bundle,
        service_url=os.environ.get("RNDS_API_URL", ""),
        bundle_uri=os.environ.get("RNDS_BUNDLE_URL_PATH", ""),
    )
    return await rira_service.post_documento_clinico(json.dumps(bundle_data))


async def main():
    return await exemplo_pending()
