from .source_execution import build_connector_plan


def test_connector_plan_respects_allowed_domains_and_fields() -> None:
    plans = build_connector_plan(
        seed_name="Ravi Kumar",
        seed_city="Chennai",
        urls=["https://example.gov/record/1", "https://not-allowed.example/x"],
        allowed_domains=["example.gov"],
        allowed_fields=["name", "address"],
        source_id="gov-example",
        source_type="GOVERNMENT_PUBLIC",
    )
    assert len(plans) == 1
    assert plans[0].url == "https://example.gov/record/1"
    assert plans[0].fields == ("name", "address")
