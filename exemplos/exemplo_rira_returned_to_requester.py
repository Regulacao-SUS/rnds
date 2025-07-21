import json
import os
from datetime import datetime

from httpx import AsyncClient

from exemplos.utils import DummyCacheHandler, stringify_data
from rnds.auth import Auth
from rnds.rira import RIRA


async def exemplo_returned_to_requester() -> None:
    """Exemplo de criação de bundle com status returned_to_requester para testes de integração RNDS."""
    httpx_async_client = AsyncClient(cert=(os.getenv("CERT_FILEPATH"), os.getenv("KEY_FILEPATH")), verify=True)
    auth = Auth(
        httpx_async_client, DummyCacheHandler(), os.environ.get("RNDS_AUTH_URL"), os.environ.get("RNDS_API_URL")
    )
    data_agora = stringify_data(datetime.now())

    rira_service = RIRA(auth=auth, service_url=os.environ.get("RNDS_API_URL", ""))

    id_solicitacao = "c1256970-5464-403d-99f9-f1ef1d1f81ea--2"
    cns = "708108612093340"
    cnes_solicitante = "6994547"
    cnes_regulador = "6450091"
    codigo_sigtap = "0209010029"
    cid10 = "K922"
    rnds_id = "b297a6ba-a7dc-4e49-95a0-d33aed1321d6-r3a1"
    data = rira_service.criar_documento_returned_to_requester(
        id_paciente=cns,
        id_solicitacao=id_solicitacao,
        data_solicitacao=data_agora,
        cnes_solicitante=cnes_solicitante,
        codigo_sigtap=codigo_sigtap,
        cid10=cid10,
        cnes_regulador=cnes_regulador,
        relates_to=rnds_id,
    )
    data = json.dumps(data)

    return await rira_service.submeter_documento_clinico(data)


async def main():
    ret = await exemplo_returned_to_requester()
    print(ret)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
