from .connectors import ConnectorContext, CorporatePublicConnector, GovernmentPublicConnector, select_connector


def test_government_connector_is_selected_for_allowed_domain() -> None:
    context = ConnectorContext("gov", "GOVERNMENT_PUBLIC", ("example.gov",), ("name",))
    connector = select_connector("https://example.gov/records", context)
    assert isinstance(connector, GovernmentPublicConnector)


def test_subdomain_is_allowed() -> None:
    context = ConnectorContext("corp", "CORPORATE_PUBLIC", ("example.com",), ())
    assert CorporatePublicConnector().can_handle("https://registry.example.com/a", context)


def test_unlisted_domain_is_rejected() -> None:
    context = ConnectorContext("gov", "GOVERNMENT_PUBLIC", ("example.gov",), ())
    assert select_connector("https://example.com/records", context) is None
