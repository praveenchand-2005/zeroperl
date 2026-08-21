from datetime import datetime, timezone

from .v3_intelligence import CandidateRecord, candidate_score, detect_address_conflicts, independent_source_count, temporal_state
from .review_queue import needs_review


def test_candidate_score_rewards_name_and_location_match() -> None:
    seed = CandidateRecord(entity_type="PERSON", name="Ravi Kumar", address=None, city="Chennai")
    candidate = CandidateRecord(entity_type="PERSON", name="Ravi Kumar", address=None, city="Chennai", source_id="s1")
    assert candidate_score(seed, candidate) == 0.9


def test_conflicting_addresses_are_detected() -> None:
    records = [
        CandidateRecord("PERSON", "Ravi Kumar", "A Road", "Chennai", source_id="gov"),
        CandidateRecord("PERSON", "Ravi Kumar", "B Road", "Chennai", source_id="registry"),
    ]
    assert detect_address_conflicts(records)


def test_source_count_is_independent() -> None:
    assert independent_source_count(["gov", "gov", "registry"]) == 2


def test_temporal_state() -> None:
    now = datetime(2026, 8, 21, tzinfo=timezone.utc)
    recent = datetime(2026, 8, 1, tzinfo=timezone.utc)
    stale = datetime(2023, 1, 1, tzinfo=timezone.utc)
    assert temporal_state(recent, now) == "RECENT"
    assert temporal_state(stale, now) == "STALE"


def test_review_queue() -> None:
    assert needs_review(0.60, False)
    assert needs_review(0.95, True)
    assert not needs_review(0.95, False)
