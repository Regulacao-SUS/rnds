from rnds.rira_resources.bundle import Bundle


def test_bundle_montar_pacote_json():
    bundle = Bundle("id", "system")
    recursos = {"urn:uuid:1": {"resourceType": "Patient"}}
    ts = "2023-01-01T00:00:00"
    result = bundle.montar_pacote_json(recursos, ts)
    assert result["resourceType"] == "Bundle"
    assert result["timestamp"] == ts
