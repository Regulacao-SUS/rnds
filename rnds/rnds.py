import asyncio
from typing import Callable

import httpx

from rnds.auth import Auth


class RNDS:
    """Serviço para integração e consulta de pacientes na RNDS."""

    def __init__(self, auth: Auth, api_url: str = None) -> None:
        """Inicializa o serviço RNDS.

        Args:
            auth (Auth): Serviço de autenticação RNDS.
        """
        self.auth = auth
        self.api_url = api_url if api_url else auth.service_url

    def obter_cns_principal(self, todos_cns: list[dict]) -> str | None:
        """Obtém o CNS principal (oficial) de uma lista de identificadores.

        Args:
            todos_cns (list[dict]): Lista de identificadores CNS.

        Returns:
            str | None: CNS oficial ou o primeiro da lista.
        """
        for cns in todos_cns:
            if cns.get("use") == "official":
                return cns.get("value")
        return todos_cns[0].get("value") if todos_cns else None

    def obter_lista_cns(self, todos_cns: list[dict]) -> list[str]:
        """Obtém todos os valores CNS de uma lista de identificadores.

        Args:
            todos_cns (list[dict]): Lista de identificadores.

        Returns:
            list[str]: Lista de CNS encontrados.
        """
        return [
            identifier_info.get("value")
            for identifier_info in todos_cns
            if "cns" in identifier_info.get("system", "") and identifier_info.get("value") is not None
        ]

    async def requisitar_pessoa_rnds(self, query: str) -> httpx.Response:
        """Realiza requisição HTTP para buscar paciente na RNDS."""
        url = f"{self.api_url}fhir/r4/Patient?identifier=http://rnds.saude.gov.br/fhir/r4/NamingSystem/{query}"
        response = await self.auth.get(url)

        # Adicione esta verificação para lançar exceção em caso de erro HTTP
        if response.status_code >= 400:
            raise httpx.HTTPStatusError(
                f"HTTP error {response.status_code}", request=response.request, response=response
            )
        return response

    async def _formatar_req_parcial(self, dados, callback_parser_municipio_ibge_id):
        if not dados.get("entry", None) or not isinstance(dados.get("entry"), list):
            return None

        resource = dados.get("entry", [])[0].get("resource", {})

        if not resource:
            return None

        paciente_info = {
            "cep": None,
            "cns": self.obter_cns_principal(resource.get("identifier", [{}, {}])),
            "lista_cns": self.obter_lista_cns(resource.get("identifier", [{}, {}])),
            "cpf": None,
            "nome": resource.get("name", [{}])[0].get("text"),
            "nome_da_mae": None,
            "bairro": None,
            "numero": None,
            "municipio_id": None,
            "logradouro": None,
            "complemento": None,
            "data_nascimento": resource.get("birthDate"),
            "raca_cor": None,
            "falecido": resource.get("deceasedBoolean", False),
            "data_falecimento": None,
        }

        match resource.get("gender"):
            case "male":
                paciente_info["sexo"] = "M"
            case "female":
                paciente_info["sexo"] = "F"
            case _:
                paciente_info["sexo"] = "N"

        if isinstance(resource.get("identifier"), list):
            identifier_infos = resource.get("identifier", [{}, {}])
            for identifier_info in identifier_infos:
                if "cpf" in identifier_info.get("system", ""):
                    paciente_info["cpf"] = identifier_info.get("value")
                    break

        if isinstance(resource.get("extension"), list):
            extension_info = resource.get("extension", [{}, {}, {}, {}])
            for extension_attr in extension_info:
                if "rnds-race" in extension_attr.get("url", ""):
                    paciente_info["raca_cor"] = (
                        extension_attr.get("extension", [])[0]
                        .get("valueCodeableConcept", {})
                        .get("coding", [])[0]
                        .get("code")
                    )
                if "rnds-parent" in extension_attr.get("url", ""):
                    if (
                        extension_attr.get("extension", [])[0]
                        .get("valueCodeableConcept", {})
                        .get("coding", [])[0]
                        .get("code")
                        == "MTH"
                    ):
                        paciente_info["nome_da_mae"] = (
                            extension_attr.get("extension", [])[1].get("valueHumanName", {}).get("text", None)
                        )

        # if isinstance(resource.get("telecom"), list):
        #     paciente_info["telefone"] = resource.get("telecom", [{}])[0].get("value")

        if isinstance(resource.get("address"), list):
            address_info = resource.get("address", [{}])[0]
            paciente_info["cep"] = address_info.get("postalCode")
            if city := address_info.get("_city", {}):
                codigo_ibge = city.get("extension", [{}])[0].get("valueString")
                paciente_info["municipio_id"] = await callback_parser_municipio_ibge_id(codigo_ibge)

            paciente_info["bairro"] = address_info.get("district")
            if isinstance(address_info.get("line"), list):
                endereco_line = address_info.get("line", [None, None, None])
                try:
                    paciente_info["logradouro"] = endereco_line[0]
                    paciente_info["numero"] = endereco_line[1]
                except (IndexError, AttributeError):
                    pass

        return paciente_info

    async def buscar_pessoa(
        self,
        identificador_paciente: str,
        callback_parser_municipio_ibge_id: Callable[[str], int | str],
        full: bool = None,
    ) -> dict | None:
        """Obtém informações do paciente a partir do CPF ou CNS.

        Args:
            identificador_paciente (str): CPF ou CNS do paciente.
            callback_parser_municipio_ibge_id (Callable[[str], int | str]): Função para obter o ID do município a partir do código IBGE.
            full (bool, opcional): Se True, retorna todos os dados da resposta.

        Returns:
            dict | None: Dicionário com informações do paciente ou None se não encontrado.
        """
        identificador_paciente = identificador_paciente.replace(".", "").replace("-", "")
        if len(identificador_paciente) == 11:
            query_parameter = f"cpf%7C{identificador_paciente}"
        elif len(identificador_paciente) > 11:
            query_parameter = f"cns%7C{identificador_paciente}"
        else:
            return None

        for tentativa in range(5):
            req = await self.requisitar_pessoa_rnds(query_parameter)
            if req.is_success:
                break
            sleep_time = max((2**tentativa) / 10, 1.2)
            await asyncio.sleep(sleep_time)

        if req.is_success and full:
            return req.json()

        if not req.is_success:
            return None

        return await self._formatar_req_parcial(req.json, callback_parser_municipio_ibge_id)
