from app.memory.refusal_graph import _links_for_incident
from app.refusal_codes.catalog import catalog_rows


def test_legacy_raw_code_links_to_its_versioned_adyen_mapping():
    links = _links_for_incident(
        {"incident_id": "inc-05", "scope_json": '{"provider_id": ["adyen"], "card_brand": ["VISA"]}',
         "metrics_json": '{"decline_codes": ["05"]}'},
        catalog_rows(),
    )

    assert {link["mapping_id"] for link in links} == {"adyen-05"}
    assert links[0]["match_type"] == "RAW_RESPONSE_CODE"


def test_canonical_code_links_without_losing_provider_specific_provenance():
    links = _links_for_incident(
        {"incident_id": "inc-dlocal", "scope_json": '{"provider_id": ["dlocal"], "card_brand": ["VISA"]}',
         "metrics_json": '{"decline_codes": ["DO_NOT_HONOR"]}'},
        catalog_rows(),
    )

    assert {link["mapping_id"] for link in links} == {"dlocal-301"}
    assert links[0]["match_type"] == "NORMALIZED_CODE"
