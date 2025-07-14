import json
import os
from datetime import datetime

from httpx import AsyncClient

from exemplos.utils import DummyCacheHandler, stringify_data
from rnds.auth import Auth
from rnds.rira import RIRA


async def exemplo_booked() -> None:
    """Exemplo de criação de bundle com status booked para testes de integração RNDS."""
    httpx_async_client = AsyncClient(cert=(os.getenv("CERT_FILEPATH"), os.getenv("KEY_FILEPATH")), verify=True)
    auth = Auth(
        httpx_async_client, DummyCacheHandler(), os.environ.get("RNDS_AUTH_URL"), os.environ.get("RNDS_API_URL")
    )
    data_agora = stringify_data(datetime.now())

    rira_service = RIRA(auth=auth, service_url=os.environ.get("RNDS_API_URL", ""))

    id_solicitacao = "c1256970-5464-403d-99f9-f1ef1d1f81ea--2"
    cns = "708108612093340"
    cnes_solicitante = "6994547"
    codigo_sigtap = "0209010029"
    cid10 = "K922"
    cnes_regulador = "6689477"
    cnes_executante = "6450091"
    data_autorizacao = "2025-07-14T23:54:25-03:00"
    cbo = "225225"
    # rnds_id = "24eff5f3-99a3-415e-87b2-e9f9a9cfa712-r3a1"
    rnds_id = "49478787-30ab-41a5-bebb-416a3855ac24-r3a1"
    rnds_id = "d0723f6a-cd99-4bfb-9799-b0720eaaac2a-r3a1"
    # await rira_service.get_documento_clinico(rnds_doc_id=rnds_id)
    data = rira_service.criar_documento_booked(
        id_paciente=cns,
        id_solicitacao=id_solicitacao,
        data_solicitacao=data_agora,
        cnes_solicitante=cnes_solicitante,
        codigo_sigtap=codigo_sigtap,
        cid10=cid10,
        cnes_regulador=cnes_regulador,
        cnes_executante=cnes_executante,
        data_autorizacao=data_autorizacao,
        cbo=cbo,
        relates_to=rnds_id,
    )
    data = json.dumps(data)
    print(data)

    return await rira_service.post_documento_clinico(data)


async def main():
    ret = await exemplo_booked()
    print(ret)  # ffa80ae7-7575-4919-938d-11a06b78c082-r3a1


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
