from rnds.rira.composition import Composition


def test_composition_gerar_dict():
    comp = Composition(
        comp_status="final",
        comp_type_code="type",
        comp_category_code="cat",
        comp_subject_id="subj",
        comp_author_id="auth",
        comp_title="title",
        comp_event_code="ev",
        comp_event_performer_id="perf",
    )
    d = comp.gerar_dict("sr_ref", "app_ref", "2023-01-01T00:00:00")
    assert d["resourceType"] == "Composition"
