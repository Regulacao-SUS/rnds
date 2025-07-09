from rnds.base_auth import BaseAuth


class DummyAuth(BaseAuth):
    async def auth(self):
        return True

    async def get_token(self) -> str:
        return "token"

    async def get_headers(self) -> dict[str, str]:
        return {"Authorization": "Bearer token"}


def test_base_auth_abstract():
    dummy = DummyAuth()
    assert hasattr(dummy, "auth")
    assert hasattr(dummy, "get_token")
    assert hasattr(dummy, "get_headers")
