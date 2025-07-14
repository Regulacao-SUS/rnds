import os

import backoff
import httpx

from rnds.auth import Auth
from rnds.rira_resources.appointment import Appointment
from rnds.rira_resources.bundle import Bundle
from rnds.rira_resources.composition import Composition
from rnds.rira_resources.condition import Condition
from rnds.rira_resources.service_request import ServiceRequest


class IdentificadorPacienteNaoInformado(BaseException): ...


class RIRAException(Exception): ...


PENDING_STATUS = "pending"
RETURNED_TO_REQUESTER_STATUS = "returned-to-requester"
WAITLIST_STATUS = "waitlist"
BOOKED_STATUS = "booked"
ATTENDED_STATUS = "attended"
FULFILLED_STATUS = "fulfilled"


class RIRA:
    """Serviço principal para integração com a RNDS via bundle FHIR."""

    def __init__(
        self,
        auth: Auth,
        service_url: str,
    ) -> None:
        """Inicializa o serviço principal RIRA.

        Args:
            auth (Auth): Serviço de autenticação RNDS.
            bundle (Bundle): Serviço de bundle FHIR.
            service_url (str, opcional): URL base da API RNDS.
            bundle_uri (str, opcional): Caminho do endpoint de bundle.
        """
        self.auth = auth
        if service_url[-1] != "/":
            service_url += "/"
        self.service_url = service_url

        self.bundle_path = "fhir/r4/Bundle"
        self.composition_path = "fhir/r4/Composition"
        self.bundle_id_system = os.environ.get("BUND_ID_SYSTEM", "")

    @backoff.on_exception(backoff.expo, (httpx.TimeoutException), max_tries=3)
    async def post_documento_clinico(self, bundle_data: str) -> str:
        """Envia um documento clínico (bundle) para a RNDS.

        Args:
            bundle_data (str): Dados do bundle em formato JSON.

        Returns:
            str: ID do documento gerado pela RNDS.
        """
        headers = await self.auth.get_headers()
        url = f"{self.service_url}{self.bundle_path}"
        ret = await self.auth.client.post(url, data=bundle_data, headers=headers)
        if ret.status_code != 201:
            raise RIRAException(f"Falha ao se comunicar com o rira. [{ret.status_code}] {ret.text}")
        return ret.headers["location"].split("/")[-1]  # retorna o id gerado pela rnds

    @backoff.on_exception(backoff.expo, (httpx.TimeoutException), max_tries=3)
    async def get_documento_clinico(self, rnds_doc_id: str) -> str:
        headers = await self.auth.get_headers()
        url = f"{self.service_url}{self.composition_path}/{rnds_doc_id}"
        ret = await self.auth.client.get(url, headers=headers)
        if ret.status_code != 200:
            raise RIRAException(f"Falha ao se comunicar com o rira. [{ret.status_code}] {ret.text}")
        return ret

    def criar_documento_pending(
        self,
        id_paciente: str,
        id_solicitacao: str,
        data_solicitacao: str,
        cnes_solicitante: str,
        codigo_sigtap: str,
        cid10: str,
        relates_to: str | None = None,
    ) -> dict:
        """Evento destinado a modelar a solicitação de um serviço, bem como o estabelecimento solicitante. É o status inicial da solicitação."""

        return self.criar_documento(
            status_composition=PENDING_STATUS,
            status_appointment=WAITLIST_STATUS,
            id_paciente=id_paciente,
            id_solicitacao=id_solicitacao,
            data_solicitacao=data_solicitacao,
            cnes_solicitante=cnes_solicitante,
            codigo_sigtap=codigo_sigtap,
            cid10=cid10,
            relates_to=relates_to,
        )

    def criar_documento_returned_to_requester(
        self,
        id_paciente: str,
        id_solicitacao: str,
        data_solicitacao: str,
        cnes_solicitante: str,
        cnes_regulador: str,
        codigo_sigtap: str,
        cid10: str,
        relates_to: str | None = None,
    ) -> dict:
        """Evento destinado a modelar a devolução (feita por um estabelecimento regulador) de um serviço ao estabelecimento solicitante."""

        return self.criar_documento(
            RETURNED_TO_REQUESTER_STATUS,
            WAITLIST_STATUS,
            id_paciente=id_paciente,
            id_solicitacao=id_solicitacao,
            data_solicitacao=data_solicitacao,
            cnes_solicitante=cnes_solicitante,
            cnes_regulador=cnes_regulador,
            codigo_sigtap=codigo_sigtap,
            cid10=cid10,
            relates_to=relates_to,
        )

    def criar_documento_booked(
        self,
        id_paciente: str,
        id_solicitacao: str,
        data_solicitacao: str,
        cnes_solicitante: str,
        cnes_regulador: str,
        codigo_sigtap: str,
        cid10: str,
        cnes_executante: str,
        data_autorizacao: str,
        cbo: str,
        relates_to: str | None = None,
    ) -> dict:
        """Evento destinado a modelar o agendamento de um serviço, bem como o estabelecimento executante."""

        return self.criar_documento(
            BOOKED_STATUS,
            BOOKED_STATUS,
            id_paciente=id_paciente,
            id_solicitacao=id_solicitacao,
            data_solicitacao=data_solicitacao,
            cnes_solicitante=cnes_solicitante,
            cnes_regulador=cnes_regulador,
            codigo_sigtap=codigo_sigtap,
            cid10=cid10,
            cnes_executante=cnes_executante,
            data_autorizacao=data_autorizacao,
            cbo=cbo,
            relates_to=relates_to,
        )

    def criar_documento_attended(
        self,
        id_paciente: str,
        id_solicitacao: str,
        data_solicitacao: str,
        cnes_solicitante: str,
        cnes_regulador: str,
        codigo_sigtap: str,
        cid10: str,
        cnes_executante: str | None = None,
        data_autorizacao: str | None = None,
        cbo: str | None = None,
        data_execucao: str | None = None,
        relates_to: str | None = None,
    ) -> dict:
        """Evento destinado a modelar o atendimento de um serviço, bem como o estabelecimento executante."""

        return self.criar_documento(
            ATTENDED_STATUS,
            FULFILLED_STATUS,
            id_paciente=id_paciente,
            id_solicitacao=id_solicitacao,
            data_solicitacao=data_solicitacao,
            cnes_solicitante=cnes_solicitante,
            cnes_regulador=cnes_regulador,
            codigo_sigtap=codigo_sigtap,
            cid10=cid10,
            cnes_executante=cnes_executante,
            data_autorizacao=data_autorizacao,
            cbo=cbo,
            data_execucao=data_execucao,
            relates_to=relates_to,
        )

    def criar_documento(
        self,
        status_composition: str,
        status_appointment: str,
        id_paciente: str,
        id_solicitacao: str,
        data_solicitacao: str,
        cnes_solicitante: str,
        codigo_sigtap: str,
        cid10: str,
        cnes_regulador: str | None = None,
        cnes_executante: str | None = None,
        data_autorizacao: str | None = None,
        data_execucao: str | None = None,
        cbo: str | None = None,
        relates_to: str | None = None,
        codigo_modalidade_assistencial: str = "09",
        codigo_carter_solicitacao: str = "routine",  # "01",
    ) -> dict:
        fullurl_regulacao_assistencial = "urn:uuid:transient-0"
        fullurl_agendamento = "urn:uuid:transient-1"
        fullurl_requisicao = "urn:uuid:transient-2"
        fullurl_cid10 = "urn:uuid:transient-3"

        bundle = Bundle(id_solicitacao, id_system=self.bundle_id_system)

        cid10 = Condition(
            cond_clinical_status_code="active",
            cond_category_code="01",
            cond_category_display="Principal",
            cond_code_code=cid10,
            cond_subject_id=id_paciente,
            cond_note_text="Sem observa\u00e7\u00f5es",
        ).gerar_dict()

        requisicao = ServiceRequest(
            sr_status="active",
            sr_intent="proposal",
            sr_category_code=codigo_modalidade_assistencial,
            sr_priority=codigo_carter_solicitacao,
            sr_code_code=codigo_sigtap,
            sr_subject_id=id_paciente,
            sr_requester_id=cnes_solicitante,
            sr_performer_type_code=cbo,
            sr_performer_id=cnes_executante,
            sr_authored_on=data_solicitacao,
        ).gerar_dict(fullurl_cid10)

        end_date = data_execucao or data_autorizacao or data_solicitacao

        agendamento = Appointment(
            app_status=status_appointment,
            app_service_category_code=codigo_modalidade_assistencial,
            app_service_type_code=codigo_sigtap,
            app_specialty_code=cbo,
            app_type_code="routine",
            app_participant_type_code="PCT",
            app_participant_status="accepted",
            app_patient_id=id_paciente,
            app_created_time=data_solicitacao,
            app_start_time=data_autorizacao,
            app_end_time=data_execucao or data_autorizacao,
        ).gerar_dict(fullurl_requisicao, fullurl_cid10)

        event_ref = fullurl_agendamento
        if status_composition == PENDING_STATUS:
            event_ref = fullurl_requisicao

        author = cnes_regulador or cnes_executante or cnes_solicitante

        regulacao_assistencial = Composition(
            comp_status="final",
            comp_type_code="RA",
            comp_category_code=codigo_modalidade_assistencial,
            comp_subject_id=id_paciente,
            comp_author_id=author,
            comp_title="Registro de Informações da Regulação Assistencial",
            comp_event_code=status_composition,
            comp_event_performer_id=author,
            comp_start=data_solicitacao,
            comp_end=end_date,
        ).gerar_dict(fullurl_agendamento, event_ref, data_solicitacao, relates_to)

        recursos = {
            fullurl_regulacao_assistencial: regulacao_assistencial,
            fullurl_agendamento: agendamento,
            fullurl_requisicao: requisicao,
            fullurl_cid10: cid10,
        }

        return bundle.montar_pacote_json(recursos, data_solicitacao)
