import pytest

from tools.criteria import check_criteria
from tools.drafting import draft_request


CASES = [
    ("pat-001", "knee MRI", "ready to submit"),
    ("pat-002", "knee MRI", "missing information"),
    ("pat-009", "knee MRI", "not covered"),
    ("pat-003", "lumbar spine MRI", "ready to submit"),
    ("pat-004", "lumbar spine MRI", "missing information"),
    ("pat-010", "lumbar spine MRI", "not covered"),
    ("pat-005", "CPAP", "ready to submit"),
    ("pat-006", "CPAP", "missing information"),
    ("pat-008", "CPAP", "not covered"),
    ("pat-007", "GLP-1", "ready to submit"),
    ("pat-003", "GLP-1", "missing information"),
    ("pat-008", "GLP-1", "not covered"),
    ("pat-005", "GLP-1", "not covered"),
    ("pat-009", "physical therapy", "ready to submit"),
    ("pat-004", "physical therapy", "missing information"),
    ("pat-010", "physical therapy", "not covered"),
]


@pytest.mark.parametrize(("patient_id", "procedure", "decision"), CASES)
def test_expected_decision(patient_id, procedure, decision):
    result = check_criteria(patient_id, procedure)
    assert result["decision"] == decision
    assert result["criteria"]


def test_ready_case_records_evidence():
    result = check_criteria("pat-001", "MRI of the knee")
    met = [item for item in result["criteria"] if item["section_id"] == "POL-KNEE-MRI-1.1"]
    assert result["decision"] == "ready to submit"
    assert met[0]["status"] == "met"
    assert met[0]["evidence"]


def test_unknown_patient():
    with pytest.raises(LookupError):
        check_criteria("pat-999", "CPAP")


def test_unknown_procedure():
    result = check_criteria("pat-001", "tattoo removal")
    assert result["error"] == "unknown procedure"
    assert result["criteria"] == []


def test_draft_ready_request_cites_policy():
    draft = draft_request("pat-005", "CPAP")
    assert draft["decision"] == "ready to submit"
    assert any(item["section_id"] == "POL-CPAP-1.1" for item in draft["citations"])
    assert "pat-005" in draft["narrative"]


def test_draft_missing_lists_gaps():
    draft = draft_request("pat-006", "CPAP")
    assert draft["decision"] == "missing information"
    assert draft["citations"]
    assert all(item["status"] == "missing" for item in draft["citations"])


def test_draft_denial_cites_exclusion():
    draft = draft_request("pat-008", "GLP-1")
    assert draft["decision"] == "not covered"
    assert any(item["section_id"] == "POL-GLP1-3.1" for item in draft["citations"])


def test_draft_unknown_procedure():
    draft = draft_request("pat-001", "tattoo removal")
    assert draft["error"] == "unknown procedure"
