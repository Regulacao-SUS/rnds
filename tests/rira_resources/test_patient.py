from rnds.rira_resources.base_resource import BaseResource
from rnds.rira_resources.patient import Patient


def test_patient_gerar_dict():
    pat = Patient()
    assert isinstance(pat, BaseResource)
