"""MCP server for the prior authorization tools.

The functions in ``tools`` stay free of MCP so tests can call them directly.
This module only registers those functions. A missing patient is returned as
an error object instead of raising, so a client can keep going.
"""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from tools.criteria import check_criteria as _check_criteria
from tools.drafting import draft_request as _draft_request
from tools.patients import get_patient as _get_patient
from tools.policies import search_policy as _search_policy

mcp = FastMCP(
    "prior-auth",
    instructions=(
        "Prepare a synthetic prior authorization. "
        "Read the chart, search the policy, check the criteria, then draft the request. "
        "Every patient and policy is fictional."
    ),
)


def _unknown_patient(patient_id: str) -> dict[str, str]:
    return {"patient_id": patient_id, "error": "unknown patient"}


@mcp.tool()
def get_patient(patient_id: str) -> dict[str, Any]:
    """Summarize one synthetic patient chart.

    Returns conditions, observations, medications, procedures, and orders.
    patient_id looks like pat-001. An unknown id returns an error object.
    """
    try:
        return _get_patient(patient_id)
    except LookupError:
        return _unknown_patient(patient_id)


@mcp.tool()
def search_policy(procedure: str, query: str, k: int = 4) -> list[dict[str, Any]]:
    """Search one payer policy and return the closest sections.

    procedure is one of: knee MRI, lumbar spine MRI, CPAP, GLP-1, physical therapy.
    query is the clinical question, such as "meniscal tear" or "AHI threshold".
    Each hit includes a section_id that can be cited. Unknown procedures and
    blank queries return an empty list.
    """
    return _search_policy(procedure, query, k=k)


@mcp.tool()
def check_criteria(patient_id: str, procedure: str) -> dict[str, Any]:
    """Check a chart against the policy for one procedure.

    Each criterion is met, not_met, or missing, with a short evidence string.
    decision is ready to submit, missing information, or not covered.
    An unknown patient returns an error object. An unknown procedure does too.
    """
    try:
        return _check_criteria(patient_id, procedure)
    except LookupError:
        return _unknown_patient(patient_id)


@mcp.tool()
def draft_request(patient_id: str, procedure: str) -> dict[str, Any]:
    """Draft a prior authorization, or explain why it cannot be submitted.

    The result includes the decision, a short narrative, and citations with
    policy section ids. An unknown patient returns an error object.
    """
    try:
        return _draft_request(patient_id, procedure)
    except LookupError:
        return _unknown_patient(patient_id)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
