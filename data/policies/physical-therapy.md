---
policy_id: POL-PT
procedure: physical therapy
also_known_as:
  - PT
  - physiotherapy
  - physical therapy evaluation and treatment
  - skilled therapy
payer: Northwind Health Plan
effective_date: 2026-01-01
status: synthetic
---

# Physical therapy

Synthetic coverage policy for an outpatient physical therapy episode for a musculoskeletal condition. This is not a real payer policy.

Apply every time window to the request date. In this dataset, treat `Bundle.timestamp` as the request date. One episode is the current course of therapy for one problem. Visits from an older, completed episode do not count toward section 3.2.

## 1. Covered indications

At least one indication in this section must be supported by the record.

### 1.1 Musculoskeletal condition with a functional limitation (POL-PT-1.1)

Physical therapy is covered when a musculoskeletal diagnosis is active and the chart documents a functional limitation. Any one of the following is enough: difficulty walking, difficulty with stairs, difficulty with activities of daily living, a work restriction, or a current pain score of 4 or higher on a 0–10 scale. The note must also name a functional goal. General fitness is not a functional goal.

### 1.2 Recent injury or surgery with a functional deficit (POL-PT-1.2)

Physical therapy is covered when a musculoskeletal injury or surgery in the prior 90 days has a documented functional deficit and a functional goal.

## 2. Required documentation

If a covered indication is supported but any item here is missing, the request is incomplete. That outcome is missing information, not a denial.

### 2.1 Physician referral (POL-PT-2.1)

An active order (service request) for physical therapy evaluation and treatment.

### 2.2 Supporting diagnosis (POL-PT-2.2)

An active condition that skilled therapy would treat, such as knee osteoarthritis, a meniscal injury, radiculopathy, or low back pain.

### 2.3 Functional limitation or pain score (POL-PT-2.3)

A documented functional limitation or a numeric pain score from the current episode. This is the evidence for section 1, recorded as its own item so a citation can point at it.

### 2.4 Visit count for this episode (POL-PT-2.4)

The number of physical therapy visits already completed in the current episode, including zero. If the count is absent, this item is missing and the visit cap in section 3.2 cannot be applied.

## 3. Exclusions

If any exclusion applies, the request is not covered. A referral does not override an exclusion.

### 3.1 Maintenance or wellness care (POL-PT-3.1)

Physical therapy is not covered when the stated purpose is maintenance, general conditioning, or wellness, and the chart does not document a functional goal. A pain score below 4 without a functional limitation supports this exclusion.

### 3.2 Visit cap without re-evaluation (POL-PT-3.2)

Physical therapy is not covered when the patient has already completed more than 12 visits in the current episode and the chart has no re-evaluation that documents a remaining functional deficit and a new goal.

## Decision guide

Use the first matching row.

1. Any exclusion in section 3 applies: **not covered**.
2. No indication in section 1 is supported: **not covered**.
3. An indication in section 1 is supported and any item in section 2 is missing: **missing information**.
4. An indication in section 1 is supported, no exclusion applies, and every item in section 2 is present: **ready to submit**.
