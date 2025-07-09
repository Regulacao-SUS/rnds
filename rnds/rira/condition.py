import os

from rnds.rira.base_resource import BaseResource


class Condition(BaseResource):
    """Gerencia o recurso Condition (CID-10) no RNDS."""

    def __init__(
        self,
        cond_clinical_status_code: str,
        cond_category_code: str,
        cond_category_display: str,
        cond_code_code: str,
        cond_subject_id: str,
        cond_note_text: str,
        cond_profile: str = os.getenv("COND_PROFILE"),
        cond_clinical_status_system: str = os.getenv("COND_CLINICAL_STATUS_SYSTEM"),
        cond_category_system: str = os.getenv("COND_CATEGORY_SYSTEM"),
        cond_code_system: str = os.getenv("COND_CODE_SYSTEM"),
        cond_subject_system: str = os.getenv("COND_SUBJECT_SYSTEM"),
    ) -> None:
        """Inicializa o serviço de Condition.

        Args:
            cond_clinical_status_code (str): Código do status clínico.
            cond_category_code (str): Código da categoria.
            cond_category_display (str): Descrição da categoria.
            cond_code_code (str): Código CID-10.
            cond_subject_id (str): ID do paciente.
            cond_note_text (str): Observações.
            cond_profile (str, opcional): Perfil FHIR.
            cond_clinical_status_system (str, opcional): Sistema do status clínico.
            cond_category_system (str, opcional): Sistema da categoria.
            cond_code_system (str, opcional): Sistema do código CID-10.
            cond_subject_system (str, opcional): Sistema do paciente.
        """
        self.cond_profile = cond_profile
        self.cond_clinical_status_system = cond_clinical_status_system
        self.cond_clinical_status_code = cond_clinical_status_code
        self.cond_category_system = cond_category_system
        self.cond_category_code = cond_category_code
        self.cond_category_display = cond_category_display
        self.cond_code_system = cond_code_system
        self.cond_code_code = cond_code_code
        self.cond_subject_system = cond_subject_system
        self.cond_subject_id = cond_subject_id
        self.cond_note_text = cond_note_text

    def gerar_dict(self) -> dict:
        """Gera o dicionário FHIR do recurso Condition.

        Returns:
            dict: Estrutura FHIR do Condition.
        """
        return {
            "resourceType": "Condition",
            "meta": {"profile": [self.cond_profile]},
            "clinicalStatus": {
                "coding": [
                    {
                        "system": self.cond_clinical_status_system,
                        "code": self.cond_clinical_status_code,
                    }
                ]
            },
            "category": [
                {
                    "coding": [
                        {
                            "system": self.cond_category_system,
                            "code": self.cond_category_code,
                            "display": self.cond_category_display,
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": self.cond_code_system,
                        "code": self.cond_code_code,
                    }
                ]
            },
            "subject": {
                "identifier": {
                    "system": self.cond_subject_system,
                    "value": self.cond_subject_id,
                }
            },
            "note": [{"text": self.cond_note_text}],
        }
