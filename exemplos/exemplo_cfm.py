import os

import httpx
from zeep import AsyncClient
from zeep.transports import AsyncTransport

from rnds.cfm import CFMClient


class CFMService:
    """Classe auxiliar para instanciar o CFMClient com o client e chave configurados."""

    def __new__(cls) -> CFMClient:
        cert_filepath = os.environ.get("CERT_FILEPATH")
        key_filepath = os.environ.get("KEY_FILEPATH")
        wdsl_client = httpx.Client(cert=(cert_filepath, key_filepath), verify=True, timeout=3)
        httpx_client = httpx.AsyncClient(cert=(cert_filepath, key_filepath), verify=True, timeout=3)
        transport = AsyncTransport(client=httpx_client, wsdl_client=wdsl_client)
        return CFMClient(
            client=AsyncClient(
                wsdl="https://ws.cfm.org.br:8080/WebServiceConsultaMedicos/ServicoConsultaMedicos?wsdl",
                transport=transport,
            ),
            chave=os.environ.get("CFM_CHAVE", ""),
        )


async def exemplo_cfm(crm: str, uf: str) -> None:
    """Exemplo de uso do CFMClient para consultar médicos."""
    cfm_client = CFMService()
    response = await cfm_client.consulta_simples(crm, uf)
    print("Consulta simples:", response)


if __name__ == "__main__":
    import asyncio
    import sys

    try:
        asyncio.run(exemplo_cfm(sys.argv[1], sys.argv[2]))
    except Exception as e:
        print("Erro na execução do exemplo:", str(e))
        raise e
