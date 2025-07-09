from rnds.rira.condition import Condition


def test_condition_gerar_dict():
    cond = Condition(
        cond_clinical_status_code="active",
        cond_category_code="01",
        cond_category_display="Principal",
        cond_code_code="K922",
        cond_subject_id="708108612093340",
        cond_note_text="Sem observações",
    )
    d = cond.gerar_dict()
    assert d["resourceType"] == "Condition"
