from rnds.rira.base_resource import BaseResource


class DummyResource(BaseResource):
    def gerar_dict(self, *args, **kwargs):
        return {"ok": True}


def test_gerar_dict():
    dummy = DummyResource()
    assert dummy.gerar_dict() == {"ok": True}
