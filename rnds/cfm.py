from zeep import AsyncClient, exceptions, helpers


class CFMClient:
    """Classe responsável pela integração com o Webservice do CFM.

    Parâmetros esperados:
        crm: até 7 dígitos
        cpf: sem máscara
        data de nascimento: DD/MM/YYYY
        UF: sigla
    """

    def __init__(self, client: AsyncClient, chave: str) -> None:
        """Inicializa o cliente CFM com o WSDL e transporte assíncrono."""
        self.client = client
        self.__chave = chave

    async def validar(self, crm: int, uf: str, cpf: str, datanascimento: str):
        """Valida um médico no serviço do CFM.

        Args:
            crm (int): Número do CRM (até 7 dígitos).
            uf (str): Sigla da UF.
            cpf (str): CPF sem máscara.
            datanascimento (str): Data de nascimento no formato DD/MM/YYYY.

        Returns:
            dict | bool: Dados serializados do médico ou False em caso de erro.
        """
        try:
            return helpers.serialize_object(
                await self.client.service.Validar(crm, uf, cpf, datanascimento, self.__chave)
            )
        except exceptions.Fault:
            return False

    async def consulta_simples(self, crm: int, uf: str):
        """Consulta simples de médico pelo CRM e UF.

        Args:
            crm (int): Número do CRM.
            uf (str): Sigla da UF.

        Returns:
            dict: Dados serializados do médico.
        """
        return helpers.serialize_object(await self.client.service.Consultar(crm, uf, self.__chave))

    async def consulta_completa(self, crm: int, uf: str, cpf: str, datanascimento: str):
        """Consulta completa de médico pelo CRM, UF, CPF e data de nascimento.

        Args:
            crm (int): Número do CRM.
            uf (str): Sigla da UF.
            cpf (str): CPF sem máscara.
            datanascimento (str): Data de nascimento no formato DD/MM/YYYY.

        Returns:
            dict: Dados serializados do médico.
        """
        return helpers.serialize_object(
            await self.client.service.ConsultaCompleta(crm, uf, cpf, datanascimento, self.__chave)
        )
