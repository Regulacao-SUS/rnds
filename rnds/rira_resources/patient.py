from rnds.rira_resources.base_resource import BaseResource


class Patient(BaseResource):
    """Gerencia o recurso Patient (Indivíduo) no RNDS."""

    def gerar_dict(self, *args, **kwargs) -> dict:
        """Gera o dicionário FHIR do recurso Patient.

        Returns:
            dict: Estrutura FHIR do Patient.
        """
