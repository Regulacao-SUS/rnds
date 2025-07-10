import os

import httpx

from rnds.auth import Auth
from rnds.rnds import RNDS


class DummyCacheHandler:
    """Classe dummy para simular o cache de tokens."""

    def __init__(self):
        self.cache = {}

    def get(self, key: str) -> str | None:
        return self.cache.get(key)

    def set(self, key: str, value: str, seconds: int) -> None:
        self.cache[key] = value


class RNDSService:
    def __new__(cls) -> RNDS:
        """Classe auxiliar para instanciar o RNDS com o Auth configurado."""
        cert_filepath = os.environ.get("CERT_FILEPATH")
        key_filepath = os.environ.get("KEY_FILEPATH")
        auth_service = Auth(
            client=httpx.AsyncClient(cert=(cert_filepath, key_filepath), verify=True),
            cache_handler=DummyCacheHandler(),
            auth_url=os.getenv("RNDS_AUTH_URL"),
            service_url=os.getenv("RNDS_API_URL"),
        )
        return RNDS(auth_service)


async def aget_municipio_id(codigo_ibge: str) -> str:
    return codigo_ibge  # Exemplo de ID de município


async def exemplo_rnds(cpf: str) -> None:
    """Exemplo de uso do RNDS para consultar pessoa."""
    rnds_client = RNDSService()
    pessoa = await rnds_client.get_pessoa(cpf, aget_municipio_id)
    print("Dados da pessoa:", pessoa)


if __name__ == "__main__":
    import asyncio
    import sys

    try:
        asyncio.run(exemplo_rnds(sys.argv[1]))
    except Exception as e:
        print("Erro na execução do exemplo:", str(e))
        raise e
