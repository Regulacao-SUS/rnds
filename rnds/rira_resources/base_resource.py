from abc import ABC, abstractmethod


class BaseResource(ABC):
    """Classe base abstrata para serviços de recursos FHIR."""

    @abstractmethod
    def gerar_dict(self, *args, **kwargs) -> dict:
        """Gera o dicionário FHIR do recurso.

        Returns:
            dict: Estrutura FHIR do recurso.
        """
