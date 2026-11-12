---
policy_id: POL-KNEE-MRI
procedure: knee MRI
also_known_as:
  - MRI knee
  - MRI of the knee
  - magnetic resonance imaging of the knee
  - knee MRI without contrast
payer: Northwind Health Plan
effective_date: 2026-01-01
status: synthetic
---

# Knee MRI

Synthetic coverage policy for magnetic resonance imaging of the knee without contrast. This is not a real payer policy. No real patient data is used with it.

Apply every time window to the request date. In this dataset, treat `Bundle.timestamp` as the request date.

## 1. Covered indications

At least one indication in this section must be supported by the record.

### 1.1 Suspected meniscal tear with mechanical symptoms (POL-KNEE-MRI-1.1)

MRI of the knee is covered when the record supports a suspected or confirmed meniscal tear and at least one mechanical symptom: locking, catching, or giving way. Joint-line tenderness or pain alone is not a mechanical symptom.

### 1.2 Ligament injury with instability (POL-KNEE-MRI-1.2)

MRI of the knee is covered when the record supports a suspected ligament injury, including ACL or collateral ligament injury, and the exam documents joint instability or a positive ligament test.

### 1.3 Locked knee (POL-KNEE-MRI-1.3)

MRI of the knee is covered when the knee is truly locked, meaning the patient cannot fully extend it because of a mechanical block. Intermittent catching is indication 1.1, not 1.3. A locked knee is a red flag: the conservative-care requirement in section 2.3 does not apply.

## 2. Required documentation

Every item in this section must be present before the request is complete. If a covered indication is supported but any applicable item here is missing, the request is incomplete. That outcome is missing information, not a denial. Section 2.3 is waived only when indication 1.3 is met.

### 2.1 History and exam (POL-KNEE-MRI-2.1)

A clinical note must document the knee diagnosis and must state whether the knee locks, catches, gives way, or is unstable.

### 2.2 Recent plain radiograph (POL-KNEE-MRI-2.2)

A knee x-ray performed within 12 months before the request, with a written report. For a suspected internal derangement, the report must be negative or inconclusive, or must say that the x-ray does not explain the mechanical symptoms.

### 2.3 Conservative care (POL-KNEE-MRI-2.3)

At least six weeks of conservative care before the request, unless indication 1.3 is met. Conservative care means physical therapy, a prescription-strength NSAID, or both, started at least six weeks before the request date. Acetaminophen alone does not count. A course that started less than six weeks before the request does not count.

## 3. Exclusions

If any exclusion applies, the request is not covered. Exclusions override documentation in section 2.

### 3.1 Uncomplicated osteoarthritis (POL-KNEE-MRI-3.1)

Knee MRI is not covered for osteoarthritis when the record documents neither mechanical symptoms (locking, catching, giving way) nor instability. Pain, swelling, and difficulty with stairs or walking do not meet section 1.

### 3.2 Repeat MRI (POL-KNEE-MRI-3.2)

Knee MRI is not covered when a knee MRI was completed in the prior six months and the record documents no new clinical findings since that study.

## Decision guide

Use the first matching row.

1. Any exclusion in section 3 applies: **not covered**.
2. No indication in section 1 is supported: **not covered**.
3. An indication in section 1 is supported and any applicable item in section 2 is missing: **missing information**.
4. An indication in section 1 is supported, no exclusion applies, and every applicable item in section 2 is present: **ready to submit**.
