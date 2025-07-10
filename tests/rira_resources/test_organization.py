from rnds.rira_resources.base_resource import BaseResource
from rnds.rira_resources.organization import Organization


def test_organization_gerar_dict():
    org = Organization()
    assert isinstance(org, BaseResource)
    assert hasattr(org, "gerar_dict")
