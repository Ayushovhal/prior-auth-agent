"""Deterministic criteria checks.

The model is not asked to decide coverage. These rules follow the decision
guide in each policy so the same chart always produces the same result.
A mentioned fact counts only when the chart affirms it. "Denies catching"
is not catching.
"""

from __future__ import annotations

import re
from datetime import date
from typing import Any

from tools.catalog import resolve_procedure
from tools.patients import as_of_date, chart_text, get_patient, parse_date

_NEGATION = re.compile(
    r"\b(no|not|without|denies|denied|negative for|negative)\b",
    re.IGNORECASE,
)


def _affirmed(text: str, phrase: str) -> bool:
    """True when a phrase appears in a sentence that does not negate it."""
    if not text:
        return False
    pattern = re.compile(re.escape(phrase), re.IGNORECASE)
    for match in pattern.finditer(text):
        left = max(
            text.rfind(".", 0, match.start()),
            text.rfind("\n", 0, match.start()),
            text.rfind(";", 0, match.start()),
        )
        sentence = text[left + 1 : match.start()]
        if _NEGATION.search(sentence):
            continue
        return True
    return False


def _any_affirmed(text: str, phrases: tuple[str, ...]) -> bool:
    return any(_affirmed(text, phrase) for phrase in phrases)


def _days_before(as_of: date, start: date | None) -> int | None:
    if start is None:
        return None
    return (as_of - start).days


def _within(as_of: date, when: date | None, days: int) -> bool:
    age = _days_before(as_of, when)
    return age is not None and 0 <= age <= days


def _items_text(items: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for item in items:
        parts.extend(
            [
                item.get("name") or "",
                item.get("note") or "",
                item.get("dosage") or "",
                item.get("value") if isinstance(item.get("value"), str) else "",
            ]
        )
    return "\n".join(part for part in parts if part)


def _criterion(
    section_id: str,
    name: str,
    status: str,
    evidence: str,
) -> dict[str, str]:
    return {
        "section_id": section_id,
        "name": name,
        "status": status,
        "evidence": evidence,
    }


def _decide(criteria: list[dict[str, str]], exclusions: list[str], indications: list[str], required: list[str]) -> str:
    if any(item["section_id"] in exclusions and item["status"] == "met" for item in criteria):
        return "not covered"
    indication_met = any(
        item["section_id"] in indications and item["status"] == "met" for item in criteria
    )
    if not indication_met:
        return "not covered"
    if any(item["section_id"] in required and item["status"] == "missing" for item in criteria):
        return "missing information"
    return "ready to submit"


def _knee(summary: dict[str, Any]) -> dict[str, Any]:
    as_of = as_of_date(summary)
    text = chart_text(summary)
    conditions = _items_text(summary["conditions"])
    meniscus = _any_affirmed(conditions + "\n" + text, ("meniscal", "meniscus"))
    mechanical = _any_affirmed(text, ("catching", "giving way", "locking"))
    ligament = _any_affirmed(text, ("ligament injury", "acl"))
    unstable = _any_affirmed(text, ("instability", "unstable", "positive ligament"))
    locked = _affirmed(text, "locked") and _any_affirmed(
        text, ("cannot fully extend", "mechanical block")
    )
    exam_text = _items_text(
        [item for item in summary["observations"] if "exam" in item["name"].lower() or "knee" in item["name"].lower()]
    )
    exam_documented = any(
        word in exam_text.lower()
        for word in ("lock", "catch", "giving way", "instability", "unstable")
    )
    xrays = [
        item
        for item in summary["observations"] + summary["procedures"]
        if "x-ray" in (item.get("name") or "").lower() or "radiologic" in (item.get("name") or "").lower()
    ]
    xray = next((item for item in xrays if _within(as_of, parse_date(item.get("date") or item.get("start")), 365)), None)
    nsaid_starts = []
    for med in summary["medications"]:
        blob = f"{med['name']} {med['dosage']} {med['note']}".lower()
        if any(word in blob for word in ("as needed", "over-the-counter", "acetaminophen")):
            continue
        if any(drug in blob for drug in ("ibuprofen", "naproxen")):
            nsaid_starts.append(parse_date(med["authored_on"]))
    pt_starts = [
        parse_date(item["start"])
        for item in summary["procedures"]
        if "therapeutic" in item["name"].lower() or "physical therapy" in item["name"].lower()
    ]
    care_starts = [day for day in nsaid_starts + pt_starts if day is not None]
    care_age = max((_days_before(as_of, day) or -1) for day in care_starts) if care_starts else None
    prior_mri = any(
        "mri" in item["name"].lower() and "knee" in (item["name"] + item["note"]).lower()
        and _within(as_of, parse_date(item.get("start")), 180)
        for item in summary["procedures"]
    )
    oa_only = _affirmed(conditions, "osteoarthritis") and not mechanical and not unstable and not locked
    criteria = [
        _criterion(
            "POL-KNEE-MRI-1.1",
            "Suspected meniscal tear with mechanical symptoms",
            "met" if meniscus and mechanical else "not_met",
            "Meniscal tear with catching, locking, or giving way." if meniscus and mechanical else "No affirmed meniscal tear with mechanical symptoms.",
        ),
        _criterion(
            "POL-KNEE-MRI-1.2",
            "Ligament injury with instability",
            "met" if ligament and unstable else "not_met",
            "Ligament injury with instability." if ligament and unstable else "No affirmed ligament instability.",
        ),
        _criterion(
            "POL-KNEE-MRI-1.3",
            "Locked knee",
            "met" if locked else "not_met",
            "Knee is locked." if locked else "Knee is not described as locked.",
        ),
        _criterion(
            "POL-KNEE-MRI-2.1",
            "History and exam",
            "met" if exam_documented else "missing",
            "Exam records locking, catching, giving way, or instability." if exam_documented else "No knee exam documents those findings.",
        ),
        _criterion(
            "POL-KNEE-MRI-2.2",
            "Recent plain radiograph",
            "met" if xray else "missing",
            f"Knee x-ray dated {xray.get('date') or xray.get('start')}." if xray else "No knee x-ray within 12 months.",
        ),
        _criterion(
            "POL-KNEE-MRI-2.3",
            "Conservative care",
            "met" if locked or (care_age is not None and care_age >= 42) else "missing",
            "Locked knee waives conservative care." if locked else (
                f"Conservative care started {care_age} days before the request." if care_age is not None else "No physical therapy or prescription-strength NSAID."
            ),
        ),
        _criterion(
            "POL-KNEE-MRI-3.1",
            "Uncomplicated osteoarthritis",
            "met" if oa_only else "not_met",
            "Osteoarthritis without mechanical symptoms or instability." if oa_only else "Uncomplicated osteoarthritis exclusion does not apply.",
        ),
        _criterion(
            "POL-KNEE-MRI-3.2",
            "Repeat MRI",
            "met" if prior_mri else "not_met",
            "Knee MRI already done in the past 6 months." if prior_mri else "No knee MRI in the past 6 months.",
        ),
    ]
    required = ["POL-KNEE-MRI-2.1", "POL-KNEE-MRI-2.2"]
    if not locked:
        required.append("POL-KNEE-MRI-2.3")
    return _result(
        summary,
        "knee MRI",
        criteria,
        _decide(criteria, ["POL-KNEE-MRI-3.1", "POL-KNEE-MRI-3.2"], ["POL-KNEE-MRI-1.1", "POL-KNEE-MRI-1.2", "POL-KNEE-MRI-1.3"], required),
    )


def _lumbar(summary: dict[str, Any]) -> dict[str, Any]:
    as_of = as_of_date(summary)
    text = chart_text(summary)
    radicular = _any_affirmed(text, ("radiculopathy", "radiating", "calf", "l5"))
    deficit = _any_affirmed(
        text,
        ("4/5", "diminished", "decreased sensation", "weakness", "sensory loss"),
    )
    red_flag = _any_affirmed(
        text,
        ("saddle anesthesia", "bowel or bladder dysfunction", "progressive bilateral"),
    )
    neuro = next(
        (item for item in summary["observations"] if item["name"].lower() == "neurologic examination"),
        None,
    )
    care_starts: list[date] = []
    for med in summary["medications"]:
        blob = f"{med['name']} {med['dosage']} {med['note']}".lower()
        if "as needed" in blob or "over-the-counter" in blob or "200 mg" in blob:
            continue
        if "naproxen" in blob or "ibuprofen" in blob:
            started = parse_date(med["authored_on"])
            if started:
                care_starts.append(started)
    for item in summary["procedures"]:
        if "therapeutic" in item["name"].lower():
            started = parse_date(item["start"])
            if started:
                care_starts.append(started)
    care_age = max((_days_before(as_of, day) or -1) for day in care_starts) if care_starts else None
    failed_care = radicular and care_age is not None and care_age >= 42
    onset_dates = [
        parse_date(item["onset"])
        for item in summary["conditions"]
        if "radiculopathy" in item["name"].lower() or "back" in item["name"].lower()
    ]
    duration_known = any(day is not None for day in onset_dates) or "week" in text.lower()
    treatment_known = care_age is not None
    acute = False
    back_onset = next(
        (parse_date(item["onset"]) for item in summary["conditions"] if "back" in item["name"].lower() or "radiculopathy" in item["name"].lower()),
        None,
    )
    if back_onset is not None:
        acute = (_days_before(as_of, back_onset) or 999) < 42 and not deficit and not red_flag
    axial_only = not radicular and not deficit
    criteria = [
        _criterion("POL-LUMBAR-MRI-1.1", "Radiculopathy with a neurologic deficit", "met" if radicular and deficit else "not_met", "Radiculopathy with a documented deficit." if radicular and deficit else "No radiculopathy with a neurologic deficit."),
        _criterion("POL-LUMBAR-MRI-1.2", "Red-flag neurologic features", "met" if red_flag else "not_met", "Red-flag features are documented." if red_flag else "No affirmed red-flag features."),
        _criterion("POL-LUMBAR-MRI-1.3", "Radicular pain after failed conservative care", "met" if failed_care else "not_met", "Radicular pain persisted after at least six weeks of care." if failed_care else "Six weeks of failed care for radicular pain is not documented."),
        _criterion("POL-LUMBAR-MRI-2.1", "Neurologic examination", "met" if neuro else "missing", neuro["value"] if neuro else "No neurologic examination is in the chart."),
        _criterion("POL-LUMBAR-MRI-2.2", "Symptom duration and conservative treatment", "met" if red_flag or (duration_known and treatment_known) else "missing", "Duration and conservative treatment are recorded." if duration_known and treatment_known else "Duration or conservative treatment is missing."),
        _criterion("POL-LUMBAR-MRI-3.1", "Acute nonspecific low back pain", "met" if acute and not radicular else "not_met", "Pain is under six weeks without a deficit or red flag." if acute and not radicular else "Acute nonspecific exclusion does not apply."),
        _criterion("POL-LUMBAR-MRI-3.2", "Axial pain without neurologic signs", "met" if axial_only else "not_met", "Pain is axial, without radicular symptoms or a deficit." if axial_only else "Axial-pain exclusion does not apply."),
    ]
    required = ["POL-LUMBAR-MRI-2.1"]
    if not red_flag:
        required.append("POL-LUMBAR-MRI-2.2")
    return _result(
        summary,
        "lumbar spine MRI",
        criteria,
        _decide(criteria, ["POL-LUMBAR-MRI-3.1", "POL-LUMBAR-MRI-3.2"], ["POL-LUMBAR-MRI-1.1", "POL-LUMBAR-MRI-1.2", "POL-LUMBAR-MRI-1.3"], required),
    )


def _number(summary: dict[str, Any], name_part: str) -> tuple[float | None, str | None]:
    for item in summary["observations"]:
        if name_part.lower() in item["name"].lower() and isinstance(item["value"], (int, float)):
            return float(item["value"]), item["date"]
    return None, None


def _cpap(summary: dict[str, Any]) -> dict[str, Any]:
    text = chart_text(summary)
    ahi, ahi_date = _number(summary, "apnea hypopnea")
    epworth, _epworth_date = _number(summary, "epworth")
    symptoms = (epworth is not None and epworth >= 10) or _any_affirmed(
        text, ("daytime somnolence", "daytime sleepiness", "witnessed apneas")
    )
    face = any("face-to-face" in item["name"].lower() for item in summary["observations"])
    order = any("cpap" in item["name"].lower() for item in summary["service_requests"])
    study = ahi is not None
    indicated = ahi is not None and (ahi >= 15 or (ahi >= 5 and symptoms))
    low_ahi = ahi is not None and ahi < 5
    central = _affirmed(text, "central sleep apnea")
    criteria = [
        _criterion("POL-CPAP-1.1", "Obstructive sleep apnea on a sleep study", "met" if indicated else "not_met", f"Obstructive AHI {ahi} on {ahi_date}." if ahi is not None else "No numeric obstructive AHI."),
        _criterion("POL-CPAP-2.1", "Sleep study with a numeric AHI", "met" if study else "missing", f"AHI {ahi}." if study else "No sleep study with a numeric AHI."),
        _criterion("POL-CPAP-2.2", "Face-to-face symptom evaluation", "met" if face else "missing", "Face-to-face sleep evaluation is present." if face else "No face-to-face sleep evaluation."),
        _criterion("POL-CPAP-2.3", "Order for CPAP", "met" if order else "missing", "Active CPAP order is present." if order else "No CPAP order."),
        _criterion("POL-CPAP-3.1", "AHI below 5", "met" if low_ahi else "not_met", f"AHI {ahi} is below 5." if low_ahi else "AHI is not below 5."),
        _criterion("POL-CPAP-3.2", "Central sleep apnea only", "met" if central else "not_met", "Central sleep apnea is the finding." if central else "Central sleep apnea exclusion does not apply."),
    ]
    if low_ahi or central:
        decision = "not covered"
    elif not study or not face or not order:
        decision = "missing information"
    elif indicated:
        decision = "ready to submit"
    else:
        decision = "not covered"
    return _result(summary, "CPAP", criteria, decision)


def _thyroid(text: str) -> str:
    if "medullary thyroid" not in text.lower() and "men 2" not in text.lower():
        return "missing"
    if _affirmed(text, "medullary thyroid") or _affirmed(text, "multiple endocrine neoplasia type 2"):
        return "present"
    return "absent"


def _glp1(summary: dict[str, Any]) -> dict[str, Any]:
    as_of = as_of_date(summary)
    text = chart_text(summary)
    names = " ".join(item["name"].lower() for item in summary["conditions"])
    type1 = "type 1" in names
    type2 = "type 2" in names
    a1c_item = next(
        (
            item
            for item in summary["observations"]
            if "a1c" in item["name"].lower() and isinstance(item["value"], (int, float))
        ),
        None,
    )
    a1c_recent = bool(a1c_item and _within(as_of, parse_date(a1c_item["date"]), 90))
    a1c_value = float(a1c_item["value"]) if a1c_item else None
    metformin = any(
        "metformin" in item["name"].lower() and item["status"] == "active"
        for item in summary["medications"]
    )
    contraindicated = _any_affirmed(text, ("metformin is contraindicated", "metformin not tolerated", "unable to take metformin"))
    bmi, bmi_date = _number(summary, "body mass index")
    bmi_recent = bmi is not None and _within(as_of, parse_date(bmi_date), 365)
    thyroid_text = "\n".join(
        part
        for item in summary["conditions"] + summary["observations"]
        for part in (item.get("note") or "", item.get("value") if isinstance(item.get("value"), str) else "")
        if part
    )
    thyroid = _thyroid(thyroid_text)
    indicated = type2 and ((a1c_recent and a1c_value is not None and a1c_value >= 7) or contraindicated)
    criteria = [
        _criterion("POL-GLP1-1.1", "Type 2 diabetes with inadequate control", "met" if indicated else "not_met", f"A1c {a1c_value} within 90 days." if indicated else "Current inadequate control is not documented."),
        _criterion("POL-GLP1-2.1", "Active type 2 diabetes", "met" if type2 else "missing", "Type 2 diabetes is on the problem list." if type2 else "Type 2 diabetes is not on the problem list."),
        _criterion("POL-GLP1-2.2", "Hemoglobin A1c within 90 days", "met" if a1c_recent else "missing", f"A1c {a1c_value} on {a1c_item['date']}." if a1c_recent and a1c_item else "No A1c within 90 days."),
        _criterion("POL-GLP1-2.3", "Metformin use or a documented reason not to use it", "met" if metformin or contraindicated else "missing", "Metformin is active." if metformin else "No metformin order or documented reason not to use it."),
        _criterion("POL-GLP1-2.4", "Body mass index", "met" if bmi_recent else "missing", f"BMI {bmi} on {bmi_date}." if bmi_recent else "No BMI within 12 months."),
        _criterion("POL-GLP1-2.5", "Thyroid safety history", "met" if thyroid in ("absent", "present") else "missing", "Thyroid history is documented." if thyroid != "missing" else "Thyroid history is not stated."),
        _criterion("POL-GLP1-3.1", "Type 1 diabetes", "met" if type1 else "not_met", "Type 1 diabetes is on the problem list." if type1 else "Not type 1 diabetes."),
        _criterion("POL-GLP1-3.2", "Medullary thyroid carcinoma or MEN 2", "met" if thyroid == "present" else "not_met", "Medullary thyroid carcinoma or MEN 2 is documented." if thyroid == "present" else "No positive medullary thyroid or MEN 2 history."),
        _criterion("POL-GLP1-3.3", "Weight loss without type 2 diabetes", "met" if not type2 and not type1 else "not_met", "No type 2 diabetes." if not type2 and not type1 else "Weight-loss-only exclusion does not apply."),
    ]
    if type1 or thyroid == "present" or (not type2):
        decision = "not covered"
    elif any(item["status"] == "missing" for item in criteria if item["section_id"].startswith("POL-GLP1-2.")):
        decision = "missing information"
    elif indicated:
        decision = "ready to submit"
    else:
        decision = "not covered"
    return _result(summary, "GLP-1", criteria, decision)


def _pt(summary: dict[str, Any]) -> dict[str, Any]:
    text = chart_text(summary)
    pain, _pain_date = _number(summary, "pain severity")
    goal = _affirmed(text, "functional goal")
    limitation = goal or _any_affirmed(text, ("difficulty", "limited", "cannot squat", "walking is limited"))
    diagnosis = bool(summary["conditions"])
    indicated = diagnosis and (limitation or (pain is not None and pain >= 4)) and goal
    referral = any(
        "physical therapy" in item["name"].lower() or "therapeutic" in item["name"].lower()
        for item in summary["service_requests"]
    )
    visits_item = next(
        (item for item in summary["observations"] if "physical therapy visits" in item["name"].lower()),
        None,
    )
    visits = visits_item["value"] if visits_item and isinstance(visits_item["value"], int) else None
    reevaluation = _affirmed(text, "re-evaluation")
    wellness = _any_affirmed(text, ("general wellness", "general conditioning", "maintenance")) and not goal
    over_cap = visits is not None and visits > 12 and not reevaluation
    criteria = [
        _criterion("POL-PT-1.1", "Musculoskeletal condition with a functional limitation", "met" if indicated else "not_met", "Diagnosis, functional goal, and limitation or pain of at least 4 are documented." if indicated else "Functional indication is not met."),
        _criterion("POL-PT-1.2", "Recent injury or surgery with a functional deficit", "not_met", "No injury or surgery in the past 90 days is used for this request."),
        _criterion("POL-PT-2.1", "Physician referral", "met" if referral else "missing", "Active physical therapy order is present." if referral else "No physical therapy referral."),
        _criterion("POL-PT-2.2", "Supporting diagnosis", "met" if diagnosis else "missing", "An active condition is present." if diagnosis else "No supporting diagnosis."),
        _criterion("POL-PT-2.3", "Functional limitation or pain score", "met" if limitation or pain is not None else "missing", f"Pain score {pain}." if pain is not None else "Functional limitation is documented." if limitation else "No functional limitation or pain score."),
        _criterion("POL-PT-2.4", "Visit count for this episode", "met" if visits is not None else "missing", f"{visits} visits in this episode." if visits is not None else "Visit count is missing."),
        _criterion("POL-PT-3.1", "Maintenance or wellness care", "met" if wellness else "not_met", "Request is for wellness or conditioning without a functional goal." if wellness else "Wellness exclusion does not apply."),
        _criterion("POL-PT-3.2", "Visit cap without re-evaluation", "met" if over_cap else "not_met", f"{visits} visits without a re-evaluation." if over_cap else "Visit cap does not apply."),
    ]
    return _result(
        summary,
        "physical therapy",
        criteria,
        _decide(criteria, ["POL-PT-3.1", "POL-PT-3.2"], ["POL-PT-1.1", "POL-PT-1.2"], ["POL-PT-2.1", "POL-PT-2.2", "POL-PT-2.3", "POL-PT-2.4"]),
    )


_CHECKERS = {
    "knee MRI": _knee,
    "lumbar spine MRI": _lumbar,
    "CPAP": _cpap,
    "GLP-1": _glp1,
    "physical therapy": _pt,
}


def _result(summary: dict[str, Any], procedure: str, criteria: list[dict[str, str]], decision: str) -> dict[str, Any]:
    return {
        "patient_id": summary["patient_id"],
        "procedure": procedure,
        "decision": decision,
        "criteria": criteria,
    }


def check_criteria(patient_id: str, procedure: str) -> dict[str, Any]:
    """Return met, not met, and missing criteria for one request.

    Raises ``LookupError`` for an unknown patient. An unknown procedure
    returns an error and no criteria.
    """
    summary = get_patient(patient_id)
    canonical = resolve_procedure(procedure)
    if canonical is None or canonical not in _CHECKERS:
        return {
            "patient_id": patient_id,
            "procedure": procedure,
            "decision": None,
            "error": "unknown procedure",
            "criteria": [],
        }
    return _CHECKERS[canonical](summary)
