---
policy_id: POL-GLP1
procedure: GLP-1
also_known_as:
  - GLP-1 receptor agonist
  - semaglutide
  - dulaglutide
  - liraglutide
  - GLP-1 medication
payer: Northwind Health Plan
effective_date: 2026-01-01
status: synthetic
---

# GLP-1 receptor agonist

Synthetic coverage policy for a GLP-1 receptor agonist (semaglutide, dulaglutide, or liraglutide) for type 2 diabetes. This is not a real payer policy. It does not cover a weight-loss-only use.

Apply every time window to the request date. In this dataset, treat `Bundle.timestamp` as the request date. This policy does not apply a renal cutoff and does not prefer one GLP-1 drug over another.

## 1. Covered indications

The indication in this section must be supported by the record. The lab used to judge control must also satisfy section 2.2. An A1c older than 90 days does not prove current control; treat that file as incomplete rather than denied.

### 1.1 Type 2 diabetes with inadequate glycemic control (POL-GLP1-1.1)

A GLP-1 receptor agonist is covered for confirmed type 2 diabetes mellitus when the most recent hemoglobin A1c that satisfies section 2.2 is at least 7.0 percent.

If metformin is documented as contraindicated or not tolerated, type 2 diabetes alone meets this indication, and the A1c threshold is not required. The chart must still contain an A1c within 90 days so the reviewer can see the current value.

## 2. Required documentation

If type 2 diabetes is present and no exclusion applies, a missing item in this section means missing information, not a denial.

### 2.1 Active type 2 diabetes (POL-GLP1-2.1)

The problem list must include type 2 diabetes mellitus. A narrative mention without a condition entry does not satisfy this item.

### 2.2 Hemoglobin A1c within 90 days (POL-GLP1-2.2)

A hemoglobin A1c result dated within 90 days before the request. An older result does not satisfy this item, even when that older result was 7.0 percent or higher.

### 2.3 Metformin use or a documented reason not to use it (POL-GLP1-2.3)

An active metformin order, or a note that metformin is contraindicated or not tolerated. Insulin alone does not satisfy this item.

### 2.4 Body mass index (POL-GLP1-2.4)

A body mass index recorded within 12 months before the request.

### 2.5 Thyroid safety history (POL-GLP1-2.5)

The chart must state whether the patient has a personal or family history of medullary thyroid carcinoma or multiple endocrine neoplasia type 2. Silence is a missing item, not a denial. A documented positive history is exclusion 3.2 instead.

## 3. Exclusions

If any exclusion applies, the request is not covered.

### 3.1 Type 1 diabetes (POL-GLP1-3.1)

A GLP-1 receptor agonist is not covered for type 1 diabetes mellitus under this policy, including when the A1c is 7.0 percent or higher and a recent lab is on file.

### 3.2 Medullary thyroid carcinoma or MEN 2 (POL-GLP1-3.2)

A GLP-1 receptor agonist is not covered when the chart documents a personal or family history of medullary thyroid carcinoma or multiple endocrine neoplasia type 2.

### 3.3 Weight loss without type 2 diabetes (POL-GLP1-3.3)

A GLP-1 receptor agonist is not covered when the request is for weight loss and the patient does not have type 2 diabetes. Body mass index, however high, does not replace the diabetes diagnosis.

## Decision guide

Use the first matching row.

1. Any exclusion in section 3 applies: **not covered**.
2. The patient does not have type 2 diabetes: **not covered**.
3. Type 2 diabetes is present, no exclusion applies, and any item in section 2 is missing: **missing information**.
4. Indication 1.1 is supported, no exclusion applies, and every item in section 2 is present: **ready to submit**.
