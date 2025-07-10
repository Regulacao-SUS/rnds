from rnds.auth import Auth


class RIRA:
    """Serviço principal para integração com a RNDS via bundle FHIR."""

    def __init__(
        self,
        auth: Auth,
        service_url: str,
        bundle_uri: str,
    ) -> None:
        """Inicializa o serviço principal RIRA.

        Args:
            auth (Auth): Serviço de autenticação RNDS.
            bundle (Bundle): Serviço de bundle FHIR.
            service_url (str, opcional): URL base da API RNDS.
            bundle_uri (str, opcional): Caminho do endpoint de bundle.
        """
        self.auth = auth
        self.service_url = service_url
        self.bundle_uri = bundle_uri

    async def test_token(self) -> str:
        """Testa e retorna o token de acesso RNDS.

        Returns:
            str: Token de acesso.
        """
        return await self.auth.get_token()

    async def post_documento_clinico(self, bundle_data: str):
        """Envia um documento clínico (bundle) para a RNDS.

        Args:
            bundle_data (str): Dados do bundle em formato JSON.

        Returns:
            httpx.Response: Resposta da requisição HTTP.
        """
        headers = await self.auth.get_headers()
        bundle_url = f"{self.service_url}{self.bundle_uri}"
        return await self.auth.client.post(bundle_url, data=bundle_data, headers=headers)
