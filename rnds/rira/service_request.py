import os
from datetime import datetime

from rnds.rira.base_resource import BaseResource


class ServiceRequest(BaseResource):
    """Gerencia o recurso ServiceRequest (Requisição de Regulação Assistencial) no RNDS."""

    def __init__(
        self,
        sr_status: str,
        sr_intent: str,
        sr_category_code: str,
        sr_priority: str,
        sr_code_code: str,
        sr_subject_id: str,
        sr_requester_id: str,
        sr_performer_type_code: str,
        sr_performer_id: str,
        sr_profile: str = os.getenv("SR_PROFILE"),
        sr_category_system: str = os.getenv("SR_CATEGORY_SYSTEM"),
        sr_code_system: str = os.getenv("SR_CODE_SYSTEM"),
        sr_subject_system: str = os.getenv("SR_SUBJECT_SYSTEM"),
        sr_authored_on: str = datetime.now().isoformat(timespec="seconds") + "-03:00",
        sr_requester_system: str = os.getenv("SR_REQUESTER_SYSTEM"),
        sr_performer_type_system: str = os.getenv("SR_PERFORMER_TYPE_SYSTEM"),
        sr_performer_system: str = os.getenv("SR_PERFORMER_SYSTEM"),
    ) -> None:
        """Inicializa o serviço de ServiceRequest.

        Args:
            sr_status (str): Status da requisição.
            sr_intent (str): Intenção da requisição.
            sr_category_code (str): Código da categoria.
            sr_priority (str): Prioridade.
            sr_code_code (str): Código do procedimento.
            sr_subject_id (str): ID do paciente.
            sr_requester_id (str): ID do solicitante.
            sr_performer_type_code (str): Código do tipo de executor.
            sr_performer_id (str): ID do executor.
            sr_profile (str, opcional): Perfil FHIR.
            sr_category_system (str, opcional): Sistema da categoria.
            sr_code_system (str, opcional): Sistema do código.
            sr_subject_system (str, opcional): Sistema do paciente.
            sr_authored_on (str, opcional): Data de autoria.
            sr_requester_system (str, opcional): Sistema do solicitante.
            sr_performer_type_system (str, opcional): Sistema do tipo de executor.
            sr_performer_system (str, opcional): Sistema do executor.
        """
        self.sr_profile = sr_profile
        self.sr_status = sr_status
        self.sr_intent = sr_intent
        self.sr_category_system = sr_category_system
        self.sr_category_code = sr_category_code
        self.sr_priority = sr_priority
        self.sr_code_system = sr_code_system
        self.sr_code_code = sr_code_code
        self.sr_subject_system = sr_subject_system
        self.sr_subject_id = sr_subject_id
        self.sr_authored_on = sr_authored_on
        self.sr_requester_system = sr_requester_system
        self.sr_requester_id = sr_requester_id
        self.sr_performer_type_system = sr_performer_type_system
        self.sr_performer_type_code = sr_performer_type_code
        self.sr_performer_system = sr_performer_system
        self.sr_performer_id = sr_performer_id

    def gerar_dict(self, condition_ref: str) -> dict:
        """Gera o dicionário FHIR do recurso ServiceRequest.

        Args:
            condition_ref (str): Referência à condição clínica (CID-10).

        Returns:
            dict: Estrutura FHIR do ServiceRequest.
        """
        return {
            "resourceType": "ServiceRequest",
            "meta": {"profile": [self.sr_profile]},
            "status": self.sr_status,
            "intent": self.sr_intent,
            "category": [
                {
                    "coding": [
                        {
                            "system": self.sr_category_system,
                            "code": self.sr_category_code,
                        }
                    ]
                }
            ],
            "priority": self.sr_priority,
            "code": {"coding": [{"system": self.sr_code_system, "code": self.sr_code_code}]},
            "subject": {
                "identifier": {
                    "system": self.sr_subject_system,
                    "value": self.sr_subject_id,
                }
            },
            "authoredOn": self.sr_authored_on,
            "requester": {
                "identifier": {
                    "system": self.sr_requester_system,
                    "value": self.sr_requester_id,
                }
            },
            "performerType": {
                "coding": [{"system": self.sr_performer_type_system, "code": self.sr_performer_type_code}]
            },
            "performer": [
                {
                    "identifier": {
                        "system": self.sr_performer_system,
                        "value": self.sr_performer_id,
                    }
                }
            ],
            "reasonReference": [{"reference": condition_ref}],
        }
