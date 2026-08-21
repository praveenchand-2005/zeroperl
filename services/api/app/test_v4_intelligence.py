from .v4_intelligence import ProfileCandidate, company_name_key, employment_state, profile_match_score, relationship_requires_review, same_company


def test_profile_match_score_rewards_name_and_location() -> None:
    candidate = ProfileCandidate("professional", "https://example.test/p", "Ravi Kumar", "Chennai", "Example Technologies", "Engineer")
    score = profile_match_score("Ravi Kumar", "Chennai", candidate)
    assert score > 0.8


def test_company_name_key_normalizes_variants() -> None:
    assert company_name_key("ABC Technologies Pvt. Ltd.") == "abctechnologiespvtltd"


def test_same_company_requires_exact_normalized_key() -> None:
    assert same_company("ABC Technologies", "ABC Technologies")
    assert not same_company("ABC Technologies", "ABC Systems")


def test_employment_state() -> None:
    assert employment_state(False, True) == "CURRENT_CANDIDATE"
    assert employment_state(True, True) == "HISTORICAL"
    assert employment_state(False, False) == "UNKNOWN"


def test_reporting_relationship_requires_higher_review_threshold() -> None:
    assert relationship_requires_review(0.85, "PUBLIC_REPORTING_RELATIONSHIP")
    assert not relationship_requires_review(0.92, "PUBLIC_REPORTING_RELATIONSHIP")
