import os


class Bundle:
    """Gerencia o pacote de recursos a ser enviado para o RNDS/EHR Services."""

    def __init__(self, bundle_id_value: str, id_system: str = os.getenv("BUND_ID_SYSTEM")) -> None:
        """Inicializa o serviço de bundle.

        Args:
            bundle_id_value (str): Valor do identificador do bundle.
            id_system (str, opcional): Sistema do identificador do bundle.
        """
        self.id_system = id_system
        self.id_value = bundle_id_value  # Replace with a generated UUID if needed

    def montar_pacote_json(self, dict_recursos: dict[str, dict], bundle_timestamp: str) -> dict:
        """Monta o bundle a ser enviado para o RNDS.

        Args:
            dict_recursos (dict[str, dict]): Dicionário de recursos a serem incluídos no bundle.
            bundle_timestamp (str): Timestamp do bundle.

        Returns:
            dict: Estrutura do bundle pronta para envio.
        """
        # TODO: algum recurso necessita de outro para formar o pacote?
        # se sim, adicionar métodos de validação que devem ser invocados aqui
        return {
            "resourceType": "Bundle",
            "identifier": {"system": self.id_system, "value": self.id_value},
            "type": "document",
            "timestamp": bundle_timestamp,
            "entry": [{"fullUrl": _id, "resource": recurso} for _id, recurso in dict_recursos.items()],
        }
