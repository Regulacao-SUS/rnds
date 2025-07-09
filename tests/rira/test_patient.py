from rnds.rira.base_resource import BaseResource
from rnds.rira.patient import Patient


def test_patient_gerar_dict():
    pat = Patient()
    assert isinstance(pat, BaseResource)
