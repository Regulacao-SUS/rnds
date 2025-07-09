from rnds.rira.service_request import ServiceRequest


def test_service_request_gerar_dict():
    sr = ServiceRequest(
        sr_status="active",
        sr_intent="proposal",
        sr_category_code="04",
        sr_priority="routine",
        sr_code_code="0209010029",
        sr_subject_id="708108612093340",
        sr_requester_id="6994547",
        sr_performer_type_code="225225",
        sr_performer_id="0440620",
    )
    d = sr.gerar_dict("cond_ref")
    assert d["resourceType"] == "ServiceRequest"
