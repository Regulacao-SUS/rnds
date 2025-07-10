from rnds.rira_resources.base_resource import BaseResource


class Organization(BaseResource):
    """Gerencia o recurso Organization (Estabelecimento de Saúde) no RNDS."""

    def gerar_dict(self, *args, **kwargs) -> dict:
        """Gera o dicionário FHIR do recurso Organization.

        Returns:
            dict: Estrutura FHIR do Organization.
        """
