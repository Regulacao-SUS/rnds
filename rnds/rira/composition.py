import os

from rnds.rira.base_resource import BaseResource


class Composition(BaseResource):
    """Gerencia o recurso Composition (Regulação Assistencial) no RNDS."""

    def __init__(
        self,
        comp_status: str,
        comp_type_code: str,
        comp_category_code: str,
        comp_subject_id: str,
        comp_author_id: str,
        comp_title: str,
        comp_event_code: str,
        comp_event_performer_id: str,
        comp_profile: str = os.getenv("COMP_PROFILE"),
        comp_type_system: str = os.getenv("COMP_TYPE_SYSTEM"),
        comp_category_system: str = os.getenv("COMP_CATEGORY_SYSTEM"),
        comp_subject_system: str = os.getenv("COMP_SUBJECT_SYSTEM"),
        comp_author_system: str = os.getenv("COMP_AUTHOR_SYSTEM"),
        comp_event_code_system: str = os.getenv("COMP_EVENT_CODE_SYSTEM"),
        comp_event_performer_system: str = os.getenv("COMP_EVENT_PERFORMER_SYSTEM"),
    ) -> None:
        """Inicializa o serviço de Composition.

        Args:
            comp_status (str): Status do Composition.
            comp_type_code (str): Código do tipo.
            comp_category_code (str): Código da categoria.
            comp_subject_id (str): ID do paciente.
            comp_author_id (str): ID do autor.
            comp_title (str): Título do documento.
            comp_event_code (str): Código do evento.
            comp_event_performer_id (str): ID do executor do evento.
            comp_profile (str, opcional): Perfil FHIR.
            comp_type_system (str, opcional): Sistema do tipo.
            comp_category_system (str, opcional): Sistema da categoria.
            comp_subject_system (str, opcional): Sistema do paciente.
            comp_author_system (str, opcional): Sistema do autor.
            comp_event_code_system (str, opcional): Sistema do código do evento.
            comp_event_performer_system (str, opcional): Sistema do executor do evento.
        """
        # Composition Parameters
        self.comp_profile = comp_profile
        self.comp_status = comp_status
        self.comp_type_system = comp_type_system
        self.comp_type_code = comp_type_code
        self.comp_category_system = comp_category_system
        self.comp_category_code = comp_category_code
        self.comp_subject_system = comp_subject_system
        self.comp_subject_id = comp_subject_id
        self.comp_author_system = comp_author_system
        self.comp_author_id = comp_author_id
        self.comp_title = comp_title  # "Registro de Informações da Regulação Assistencial"
        self.comp_event_code_system = comp_event_code_system
        self.comp_event_code = comp_event_code
        self.comp_event_performer_system = comp_event_performer_system
        self.comp_event_performer_id = comp_event_performer_id

    def gerar_dict(self, service_request_ref: str, appointment_ref: str, bundle_timestamp: str) -> dict:
        """Gera o dicionário FHIR do recurso Composition.

        Args:
            service_request_ref (str): Referência à requisição de serviço.
            appointment_ref (str): Referência ao agendamento.
            bundle_timestamp (str): Timestamp do bundle.

        Returns:
            dict: Estrutura FHIR do Composition.
        """
        return {
            "resourceType": "Composition",
            "meta": {"profile": [self.comp_profile]},
            "status": self.comp_status,
            "type": {"coding": [{"system": self.comp_type_system, "code": self.comp_type_code}]},
            "category": [
                {
                    "coding": [
                        {
                            "system": self.comp_category_system,
                            "code": self.comp_category_code,
                        }
                    ]
                }
            ],
            "subject": {
                "identifier": {
                    "system": self.comp_subject_system,
                    "value": self.comp_subject_id,
                }
            },
            "date": bundle_timestamp,
            "author": [
                {
                    "identifier": {
                        "system": self.comp_author_system,
                        "value": self.comp_author_id,
                    }
                }
            ],
            "title": self.comp_title,
            "event": [
                {
                    "code": [
                        {
                            "coding": [
                                {
                                    "system": self.comp_event_code_system,
                                    "code": self.comp_event_code,
                                }
                            ]
                        }
                    ],
                    "period": {"start": bundle_timestamp, "end": bundle_timestamp},
                    "detail": [
                        {
                            "identifier": {
                                "system": self.comp_event_performer_system,
                                "value": self.comp_event_performer_id,
                            }
                        },
                        {"reference": service_request_ref},
                    ],
                }
            ],
            "section": [{"entry": [{"reference": appointment_ref}]}],
        }
