"""FHIR chart loading.

Charts are synthetic FHIR R4 bundles. ``Bundle.timestamp`` is the request
date used by every time window in the policies.
"""

from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def patients_dir() -> Path:
    return project_root() / "data" / "patients"


def _display(concept: dict[str, Any] | None) -> str:
    if not concept:
        return ""
    if concept.get("text"):
        return str(concept["text"])
    coding = concept.get("coding") or []
    if coding:
        return str(coding[0].get("display") or coding[0].get("code") or "")
    return ""


def _notes(resource: dict[str, Any]) -> str:
    return " ".join(note.get("text", "") for note in resource.get("note") or [])


def _on_date(value: str | None) -> str | None:
    if not value:
        return None
    return value[:10]


def load_bundle(patient_id: str) -> dict[str, Any]:
    path = patients_dir() / f"{patient_id}.json"
    if not path.is_file():
        raise LookupError(f"Unknown patient: {patient_id}")
    return json.loads(path.read_text(encoding="utf-8"))


def _condition(resource: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": resource["id"],
        "name": _display(resource.get("code")),
        "onset": _on_date(resource.get("onsetDateTime")),
        "verification": _display(resource.get("verificationStatus")),
        "note": _notes(resource),
    }


def _observation(resource: dict[str, Any]) -> dict[str, Any]:
    value: float | int | str | None = None
    unit = None
    if "valueQuantity" in resource:
        value = resource["valueQuantity"].get("value")
        unit = resource["valueQuantity"].get("unit")
    elif "valueInteger" in resource:
        value = resource["valueInteger"]
    elif "valueString" in resource:
        value = resource["valueString"]
    return {
        "id": resource["id"],
        "name": _display(resource.get("code")),
        "date": _on_date(resource.get("effectiveDateTime")),
        "value": value,
        "unit": unit,
        "note": _notes(resource),
    }


def _medication(resource: dict[str, Any]) -> dict[str, Any]:
    dosage = ""
    instructions = resource.get("dosageInstruction") or []
    if instructions:
        dosage = instructions[0].get("text") or ""
    return {
        "id": resource["id"],
        "name": _display(resource.get("medicationCodeableConcept")),
        "status": resource.get("status"),
        "authored_on": _on_date(resource.get("authoredOn")),
        "dosage": dosage,
        "note": _notes(resource),
    }


def _procedure(resource: dict[str, Any]) -> dict[str, Any]:
    period = resource.get("performedPeriod") or {}
    return {
        "id": resource["id"],
        "name": _display(resource.get("code")),
        "start": _on_date(period.get("start")),
        "end": _on_date(period.get("end")),
        "note": _notes(resource),
    }


def _service_request(resource: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": resource["id"],
        "name": _display(resource.get("code")),
        "status": resource.get("status"),
        "authored_on": _on_date(resource.get("authoredOn")),
        "note": _notes(resource),
    }


def get_patient(patient_id: str) -> dict[str, Any]:
    """Return a condensed chart for one synthetic patient.

    Raises ``LookupError`` when the id does not match a bundle file.
    """
    bundle = load_bundle(patient_id)
    patient = next(
        entry["resource"]
        for entry in bundle["entry"]
        if entry["resource"]["resourceType"] == "Patient"
    )
    official = next(
        (name for name in patient.get("name") or [] if name.get("use") == "official"),
        (patient.get("name") or [{}])[0],
    )
    given = " ".join(official.get("given") or [])
    family = official.get("family") or ""
    grouped: dict[str, list[dict[str, Any]]] = {
        "Condition": [],
        "Observation": [],
        "MedicationRequest": [],
        "Procedure": [],
        "ServiceRequest": [],
    }
    builders = {
        "Condition": _condition,
        "Observation": _observation,
        "MedicationRequest": _medication,
        "Procedure": _procedure,
        "ServiceRequest": _service_request,
    }
    for entry in bundle["entry"]:
        resource = entry["resource"]
        kind = resource["resourceType"]
        if kind in builders and kind != "Patient":
            grouped[kind].append(builders[kind](resource))
    return {
        "patient_id": patient["id"],
        "name": f"{given} {family}".strip(),
        "gender": patient.get("gender"),
        "birth_date": patient.get("birthDate"),
        "as_of": _on_date(bundle.get("timestamp")),
        "conditions": grouped["Condition"],
        "observations": grouped["Observation"],
        "medications": grouped["MedicationRequest"],
        "procedures": grouped["Procedure"],
        "service_requests": grouped["ServiceRequest"],
    }


def as_of_date(summary: dict[str, Any]) -> date:
    return datetime.strptime(summary["as_of"], "%Y-%m-%d").date()


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return datetime.strptime(value[:10], "%Y-%m-%d").date()


def chart_text(summary: dict[str, Any]) -> str:
    """Flatten the chart into one string for rule checks."""
    parts: list[str] = []
    for group in (
        "conditions",
        "observations",
        "medications",
        "procedures",
        "service_requests",
    ):
        for item in summary[group]:
            parts.append(item.get("name") or "")
            parts.append(item.get("note") or "")
            parts.append(item.get("dosage") or "")
            value = item.get("value")
            if isinstance(value, str):
                parts.append(value)
    return "\n".join(part for part in parts if part)
