"""Draft a prior authorization packet from the criteria check.

Citations are the policy section ids the decision actually used. A ready
request cites the met criteria. A missing-information result cites the gaps.
A denial cites the exclusion or the unmet indication.
"""

from __future__ import annotations

from typing import Any

from tools.criteria import check_criteria


def _used(criteria: list[dict[str, str]], decision: str) -> list[dict[str, str]]:
    if decision == "ready to submit":
        return [item for item in criteria if item["status"] == "met" and not item["section_id"].endswith(("-3.1", "-3.2", "-3.3"))]
    if decision == "missing information":
        return [item for item in criteria if item["status"] == "missing"]
    exclusions = [
        item for item in criteria if item["status"] == "met" and "-3." in item["section_id"]
    ]
    if exclusions:
        return exclusions
    return [item for item in criteria if item["status"] == "not_met" and "-1." in item["section_id"]]


def draft_request(patient_id: str, procedure: str) -> dict[str, Any]:
    """Return a structured request, or the reason one cannot be submitted.

    Raises ``LookupError`` for an unknown patient.
    """
    review = check_criteria(patient_id, procedure)
    if review.get("error"):
        return review
    decision = review["decision"]
    citations = [
        {
            "section_id": item["section_id"],
            "name": item["name"],
            "status": item["status"],
            "evidence": item["evidence"],
        }
        for item in _used(review["criteria"], decision)
    ]
    if decision == "ready to submit":
        narrative = (
            f"Please authorize {procedure} for {patient_id}. "
            "The chart supports the covered indication and the required documentation is present."
        )
    elif decision == "missing information":
        gaps = "; ".join(item["name"] for item in citations)
        narrative = f"The {procedure} request for {patient_id} is incomplete. Missing: {gaps}."
    else:
        reasons = "; ".join(item["name"] for item in citations) or "no covered indication"
        narrative = f"{procedure} for {patient_id} is not covered. Reason: {reasons}."
    return {
        "patient_id": patient_id,
        "procedure": review["procedure"],
        "decision": decision,
        "narrative": narrative,
        "citations": citations,
    }
