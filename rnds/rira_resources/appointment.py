import os

from rnds.rira_resources.base_resource import BaseResource


class Appointment(BaseResource):
    """Gerencia o recurso Appointment (Agendamento de Regulação Assistencial) no RNDS."""

    def __init__(
        self,
        app_status: str,
        app_service_category_code: str,
        app_service_type_code: str,
        app_type_code: str,
        app_start_time: str,
        app_end_time: str,
        app_created_time: str,
        app_patient_id: str,
        app_participant_type_code: str,
        app_participant_status: str,
        app_specialty_code: str | None = None,
        app_profile: str = os.getenv("APP_PROFILE"),
        app_service_category_system: str = os.getenv("APP_SERVICE_CATEGORY_SYSTEM"),
        app_service_type_system: str = os.getenv("APP_SERVICE_TYPE_SYSTEM"),
        app_specialty_system: str = os.getenv("APP_SPECIALTY_SYSTEM"),
        app_type_system: str = os.getenv("APP_TYPE_SYSTEM"),
        app_patient_system: str = os.getenv("APP_PATIENT_SYSTEM"),
        app_participant_type_system: str = os.getenv("APP_PARTICIPANT_TYPE_SYSTEM"),
    ) -> None:
        """Inicializa o serviço de Appointment.

        Args:
            app_status (str): Status do agendamento.
            app_service_category_code (str): Código da categoria do serviço.
            app_service_type_code (str): Código do tipo de serviço.
            app_specialty_code (str): Código da especialidade.
            app_type_code (str): Código do tipo de agendamento.
            app_start_time (str): Data/hora de início.
            app_end_time (str): Data/hora de término.
            app_created_time (str): Data/hora de criação.
            app_patient_id (str): ID do paciente.
            app_participant_type_code (str): Código do tipo de participante.
            app_participant_status (str): Status do participante.
            app_profile (str, opcional): Perfil FHIR.
            app_service_category_system (str, opcional): Sistema da categoria do serviço.
            app_service_type_system (str, opcional): Sistema do tipo de serviço.
            app_specialty_system (str, opcional): Sistema da especialidade.
            app_type_system (str, opcional): Sistema do tipo de agendamento.
            app_patient_system (str, opcional): Sistema do paciente.
            app_participant_type_system (str, opcional): Sistema do tipo de participante.
        """
        self.app_profile = app_profile
        self.app_status = app_status
        self.app_service_category_system = app_service_category_system
        self.app_service_category_code = app_service_category_code
        self.app_service_type_system = app_service_type_system
        self.app_service_type_code = app_service_type_code
        self.app_specialty_system = app_specialty_system
        self.app_specialty_code = app_specialty_code
        self.app_type_system = app_type_system
        self.app_type_code = app_type_code
        self.app_start_time = app_start_time
        self.app_end_time = app_end_time
        self.app_created_time = app_created_time
        self.app_patient_system = app_patient_system
        self.app_patient_id = app_patient_id
        self.app_participant_type_system = app_participant_type_system
        self.app_participant_type_code = app_participant_type_code
        self.app_participant_status = app_participant_status

    def gerar_dict(self, service_request_ref: str, condition_ref: str) -> dict:
        """Gera o dicionário FHIR do recurso Appointment.

        Args:
            service_request_ref (str): Referência à requisição de serviço.
            condition_ref (str): Referência à condição clínica (CID-10).

        Returns:
            dict: Estrutura FHIR do Appointment.
        """
        data = {
            "resourceType": "Appointment",
            "meta": {"profile": [self.app_profile]},
            "status": self.app_status,
            "serviceCategory": [
                {
                    "coding": [
                        {
                            "system": self.app_service_category_system,
                            "code": self.app_service_category_code,
                        }
                    ]
                }
            ],
            "serviceType": [{"coding": [{"system": self.app_service_type_system, "code": self.app_service_type_code}]}],
            "appointmentType": {"coding": [{"system": self.app_type_system, "code": self.app_type_code}]},
            "reasonReference": [{"reference": condition_ref}],
            "start": self.app_start_time,
            "end": self.app_end_time,
            "created": self.app_created_time,
            "basedOn": [{"reference": service_request_ref}],
            "participant": [
                {
                    "type": [
                        {
                            "coding": [
                                {
                                    "system": self.app_participant_type_system,
                                    "code": self.app_participant_type_code,
                                }
                            ]
                        }
                    ],
                    "actor": {
                        "identifier": {
                            "system": self.app_patient_system,
                            "value": self.app_patient_id,
                        }
                    },
                    "status": self.app_participant_status,
                }
            ],
        }

        if self.app_specialty_code:
            data["specialty"] = [{"coding": [{"system": self.app_specialty_system, "code": self.app_specialty_code}]}]

        return data
