from tools.patients import get_patient
import pytest


def test_known_patient_summary_includes_chart_sections():
    summary = get_patient("pat-001")
    assert summary["patient_id"] == "pat-001"
    assert summary["name"] == "Elena Vasquez"
    assert summary["as_of"] == "2026-03-15"
    assert any("meniscus" in item["name"].lower() for item in summary["conditions"])
    assert summary["observations"]
    assert summary["medications"]
    assert summary["procedures"]


def test_unknown_patient():
    with pytest.raises(LookupError, match="Unknown patient"):
        get_patient("pat-999")
