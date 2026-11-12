---
policy_id: POL-CPAP
procedure: CPAP
also_known_as:
  - CPAP device
  - continuous positive airway pressure
  - CPAP for obstructive sleep apnea
  - PAP therapy
payer: Northwind Health Plan
effective_date: 2026-01-01
status: synthetic
---

# CPAP

Synthetic coverage policy for a continuous positive airway pressure (CPAP) device for obstructive sleep apnea. This is not a real payer policy.

Apply every time window to the request date. In this dataset, treat `Bundle.timestamp` as the request date.

## 1. Covered indications

The indication in this section must be supported by a sleep study in the record. Symptoms without a numeric apnea-hypopnea index do not meet it.

### 1.1 Obstructive sleep apnea on a sleep study (POL-CPAP-1.1)

CPAP is covered when a polysomnogram or a home sleep apnea test reports an obstructive apnea-hypopnea index (AHI) of at least 15 events per hour.

CPAP is also covered when that index is at least 5 and less than 15 events per hour and the face-to-face evaluation documents at least one of: daytime sleepiness, witnessed apneas, or an Epworth Sleepiness Scale score of 10 or higher.

An index under 5 does not meet this indication.

## 2. Required documentation

If the sleep study would support section 1, or if no sleep study is on file yet, missing items in this section make the request incomplete. Absence of a sleep study is missing information, not a denial.

### 2.1 Sleep study with a numeric AHI (POL-CPAP-2.1)

The chart must include a polysomnogram or a home sleep apnea test and a numeric obstructive AHI. A diagnosis label of "suspected sleep apnea" without an index does not satisfy this item.

### 2.2 Face-to-face symptom evaluation (POL-CPAP-2.2)

A face-to-face note must document sleepiness, witnessed apneas, snoring, or an Epworth Sleepiness Scale score.

### 2.3 Order for CPAP (POL-CPAP-2.3)

An active order (service request) for CPAP must be on the chart.

## 3. Exclusions

If any exclusion applies, the request is not covered. A completed study with an index under 5 is a denial, not an incomplete file.

### 3.1 AHI below 5 (POL-CPAP-3.1)

CPAP is not covered when a completed sleep study reports an obstructive AHI under 5 events per hour. Snoring with an index under 5 remains not covered.

### 3.2 Central sleep apnea only (POL-CPAP-3.2)

CPAP under this policy is not covered when the study shows central sleep apnea without obstructive events. Central apnea is outside this policy.

## Decision guide

Use the first matching row.

1. A completed study meets exclusion 3.1 or 3.2: **not covered**.
2. No sleep study is on file, or another applicable item in section 2 is missing: **missing information**. Do not deny the request only because the study has not been done.
3. Section 1 is supported, no exclusion applies, and every item in section 2 is present: **ready to submit**.
4. Otherwise: **not covered**.
