import pytest
from unittest.mock import AsyncMock, MagicMock
from rnds.rnds import RNDS
from rnds.auth import Auth
import httpx


# Fixtures para reutilização nos testes
@pytest.fixture
def mock_auth():
    auth = MagicMock(spec=Auth)
    auth.client = AsyncMock()
    return auth


@pytest.fixture
def rnds_service(mock_auth):
    return RNDS(mock_auth)


# Testes para get_cns_principal
class TestGetCnsPrincipal:
    @pytest.mark.parametrize(
        "input_data,expected",
        [
            # Caso com CNS oficial
            pytest.param([{"use": "official", "value": "123"}], "123", id="official_cns_exists"),
            # Caso sem CNS oficial (pega o primeiro)
            pytest.param([{"use": "temp", "value": "456"}, {"value": "789"}], "456", id="no_official_cns_gets_first"),
            # Caso com lista vazia
            pytest.param([], None, id="empty_list_returns_none"),
            # Caso com valor None
            pytest.param([{"use": "official", "value": None}], None, id="official_cns_with_none_value"),
        ],
    )
    def test_get_cns_principal(self, rnds_service, input_data, expected):
        """Scenario: Testar diferentes casos de obtenção do CNS principal"""
        result = rnds_service.get_cns_principal(input_data)
        assert result == expected


# Testes para get_lista_cns
class TestGetListaCns:
    @pytest.mark.parametrize(
        "input_data,expected",
        [
            # Caso com CNS exato (minúsculas)
            pytest.param(
                [{"system": "cns", "value": "123"}, {"system": "other", "value": "456"}], ["123"], id="cns_lowercase"
            ),
            # Caso com CNS em maiúsculas (não deve incluir)
            pytest.param([{"system": "CNS", "value": "789"}], [], id="cns_uppercase_not_included"),
            # Caso com string que contém "cns" mas não é exato
            pytest.param(
                [{"system": "bcns", "value": "111"}, {"system": "cns2", "value": "222"}],
                ["111", "222"],
                id="cns_not_exact_match",
            ),
            # Caso com valor None
            pytest.param(
                [{"system": "cns", "value": None}, {"system": "cns", "value": "123"}], ["123"], id="cns_with_none_value"
            ),
        ],
    )
    def test_get_lista_cns_case_sensitive(self, rnds_service, input_data, expected):
        """Scenario: Testar extração case sensitive de lista de CNS"""
        result = rnds_service.get_lista_cns(input_data)
        assert result == expected


# Testes para req_pessoa
class TestReqPessoa:
    @pytest.mark.asyncio
    async def test_req_pessoa_correct_url(self, rnds_service, mock_auth):
        """Scenario: A requisição deve usar a URL correta"""
        mock_auth.get.return_value = httpx.Response(200, json={})

        query = "test_query"
        await rnds_service.req_pessoa(query)

        expected_url = (
            f"{rnds_service.api_url}fhir/r4/Patient?identifier=http://rnds.saude.gov.br/fhir/r4/NamingSystem/{query}"
        )
        mock_auth.get.assert_called_once_with(expected_url)


# Testes para get_pessoa
class TestGetPessoa:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "input_cpf_cns,query_param",
        [
            ("123.456.789-09", "cpf%7C12345678909"),  # CPF com formatação
            ("12345678909", "cpf%7C12345678909"),  # CPF sem formatação
            ("12345678901234", "cns%7C12345678901234"),  # CNS
        ],
    )
    async def test_query_parameter_generation(self, rnds_service, mock_auth, input_cpf_cns, query_param):
        """Scenario: A geração do parâmetro de consulta deve funcionar para diferentes formatos de entrada"""
        mock_auth.get.return_value = httpx.Response(200, json={})

        await rnds_service.get_pessoa(input_cpf_cns, AsyncMock())

        expected_url = f"{rnds_service.api_url}fhir/r4/Patient?identifier=http://rnds.saude.gov.br/fhir/r4/NamingSystem/{query_param}"
        mock_auth.get.assert_called_once_with(expected_url)

    @pytest.mark.asyncio
    async def test_full_response(self, rnds_service, mock_auth):
        """Scenario: Quando full=True, deve retornar a resposta completa"""
        mock_response = {"entry": [{"resource": {"id": "123"}}]}
        mock_auth.get.return_value = httpx.Response(200, json=mock_response)

        result = await rnds_service.get_pessoa("12345678909", AsyncMock(), full=True)

        assert result == mock_response

    @pytest.mark.asyncio
    async def test_successful_response_with_data(self, rnds_service, mock_auth):
        """Scenario: Resposta bem-sucedida com dados deve retornar informações estruturadas"""
        mock_response = {
            "entry": [
                {
                    "resource": {
                        "identifier": [
                            {"use": "official", "system": "cns", "value": "123"},
                            {"system": "cpf", "value": "11122233344"},
                        ],
                        "name": [{"text": "Fulano de Tal"}],
                        "gender": "male",
                        "birthDate": "2000-01-01",
                        "extension": [
                            {"url": "rnds-race", "extension": [{"valueCodeableConcept": {"coding": [{"code": "1"}]}}]},
                            {
                                "url": "rnds-parent",
                                "extension": [
                                    {"valueCodeableConcept": {"coding": [{"code": "MTH"}]}},
                                    {"valueHumanName": {"text": "Mãe do Fulano"}},
                                ],
                            },
                        ],
                        "address": [
                            {
                                "postalCode": "12345678",
                                "_city": {"extension": [{"valueString": "1234567"}]},
                                "district": "Centro",
                                "line": ["Rua Principal", "123", "Apto 101"],
                            }
                        ],
                    }
                }
            ]
        }
        mock_auth.get.return_value = httpx.Response(200, json=mock_response)

        async def mock_get_municipio_id(codigo_ibge):
            return 1 if codigo_ibge == "1234567" else None

        result = await rnds_service.get_pessoa("11122233344", mock_get_municipio_id)

        assert result == {
            "cep": "12345678",
            "cns": "123",
            "lista_cns": ["123"],
            "cpf": "11122233344",
            "nome": "Fulano de Tal",
            "nome_da_mae": "Mãe do Fulano",
            "sexo": "M",
            "bairro": "Centro",
            "numero": "123",
            "municipio_id": 1,
            "logradouro": "Rua Principal",
            "complemento": None,
            "data_nascimento": "2000-01-01",
            "raca_cor": "1",
        }

    @pytest.mark.asyncio
    async def test_response_without_entry(self, rnds_service, mock_auth):
        """Scenario: Resposta sem entry deve retornar None"""
        mock_auth.get.return_value = httpx.Response(200, json={})

        result = await rnds_service.get_pessoa("11122233344", AsyncMock())

        assert result is None

    @pytest.mark.asyncio
    async def test_http_error(self, rnds_service, mock_auth):
        """Scenario: Erro HTTP deve propagar a exceção"""
        # Crie um request mock
        mock_request = httpx.Request("GET", "http://test.url")

        # Crie uma resposta mock com status 404 e request associado
        mock_response = httpx.Response(404, request=mock_request, json={})
        mock_auth.get.return_value = mock_response

        # Verifique se a exceção específica é lançada
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await rnds_service.get_pessoa("11122233344", AsyncMock())

        # Verifique se o status code na exceção é 404
        assert exc_info.value.response.status_code == 404

    @pytest.mark.asyncio
    async def test_gender_mapping(self, rnds_service, mock_auth):
        """Scenario: Mapeamento de gênero deve funcionar corretamente"""
        test_cases = [
            ("male", "M"),
            ("female", "F"),
            ("other", "N"),
            ("unknown", "N"),
            (None, "N"),
        ]

        for gender_input, expected in test_cases:
            mock_response = {
                "entry": [
                    {
                        "resource": {
                            "identifier": [],
                            "name": [{"text": "Test"}],
                            "gender": gender_input,
                            "birthDate": "2000-01-01",
                        }
                    }
                ]
            }
            mock_auth.get.return_value = httpx.Response(200, json=mock_response)

            result = await rnds_service.get_pessoa("11122233344", AsyncMock())
            assert result["sexo"] == expected

    @pytest.mark.asyncio
    async def test_address_parsing(self, rnds_service, mock_auth):
        """Scenario: Parsing de endereço deve lidar com diferentes formatos"""
        test_cases = [
            # Caso completo
            (
                {
                    "postalCode": "12345678",
                    "_city": {"extension": [{"valueString": "1234567"}]},
                    "district": "Centro",
                    "line": ["Rua A", "123", "Bloco B"],
                },
                {"cep": "12345678", "bairro": "Centro", "logradouro": "Rua A", "numero": "123", "municipio_id": 1},
            ),
            # Caso sem número
            (
                {"postalCode": "12345678", "district": "Centro", "line": ["Rua A"]},
                {"cep": "12345678", "bairro": "Centro", "logradouro": "Rua A", "numero": None, "municipio_id": None},
            ),
            # Caso sem cidade
            (
                {"postalCode": "12345678", "district": "Centro", "line": []},
                {"cep": "12345678", "bairro": "Centro", "logradouro": None, "numero": None, "municipio_id": None},
            ),
        ]

        async def mock_get_municipio_id(codigo_ibge):
            return 1 if codigo_ibge == "1234567" else None

        for address_input, expected in test_cases:
            mock_response = {
                "entry": [
                    {
                        "resource": {
                            "identifier": [],
                            "name": [{"text": "Test"}],
                            "gender": "male",
                            "birthDate": "2000-01-01",
                            "address": [address_input],
                        }
                    }
                ]
            }
            mock_auth.get.return_value = httpx.Response(200, json=mock_response)

            result = await rnds_service.get_pessoa("11122233344", mock_get_municipio_id)

            for key in expected:
                assert result[key] == expected[key]

    @pytest.mark.asyncio
    async def test_get_pessoa_returns_none_when_empty_entry(self, rnds_service, mock_auth):
        """Scenario: Quando 'entry' existe mas está vazio, deve retornar None"""
        # Mock da resposta com entry vazio
        mock_response = httpx.Response(200, json={"entry": []})
        mock_auth.get.return_value = mock_response

        result = await rnds_service.get_pessoa("1", AsyncMock())

        assert result is None
