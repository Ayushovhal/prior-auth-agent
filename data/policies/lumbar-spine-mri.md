---
policy_id: POL-LUMBAR-MRI
procedure: lumbar spine MRI
also_known_as:
  - lumbar MRI
  - MRI lumbar spine
  - MRI of the lumbar spine
  - lumbar spine MRI without contrast
payer: Northwind Health Plan
effective_date: 2026-01-01
status: synthetic
---

# Lumbar spine MRI

Synthetic coverage policy for magnetic resonance imaging of the lumbar spine without contrast. This is not a real payer policy.

Apply every time window to the request date. In this dataset, treat `Bundle.timestamp` as the request date.

## 1. Covered indications

At least one indication in this section must be supported by the record.

### 1.1 Radiculopathy with a neurologic deficit (POL-LUMBAR-MRI-1.1)

Lumbar MRI is covered when the record documents lumbar radiculopathy and a neurologic deficit on exam. A deficit is weakness, a diminished reflex, or a sensory loss in a radicular pattern. Pain radiating to the leg, without one of those findings, does not meet this indication.

### 1.2 Red-flag neurologic features (POL-LUMBAR-MRI-1.2)

Lumbar MRI is covered when the record documents any of the following: saddle anesthesia, bowel or bladder dysfunction attributed to the spine, or progressive bilateral leg weakness. These are red flags. When this indication is met, section 2.2 does not apply.

### 1.3 Radicular pain after failed conservative care (POL-LUMBAR-MRI-1.3)

Lumbar MRI is covered when radicular pain (pain radiating below the knee, or into a named nerve-root distribution) has persisted despite at least six weeks of conservative care. Conservative care means physical therapy, a prescription-strength NSAID, or both, started at least six weeks before the request date. Persistent pain after that course counts as failure. Axial low back pain without radiation does not meet this indication.

## 2. Required documentation

If a covered indication is supported but any applicable item here is missing, the request is incomplete. That outcome is missing information, not a denial. Section 2.2 is waived only when indication 1.2 is met.

### 2.1 Neurologic examination (POL-LUMBAR-MRI-2.1)

A neurologic exam must be recorded, including strength, reflexes, or sensation. A normal exam counts as documentation. If no exam is in the chart, this item is missing even when the patient reports leg pain.

### 2.2 Symptom duration and conservative treatment (POL-LUMBAR-MRI-2.2)

The chart must state how long the symptoms have been present and must record the conservative treatment used, unless indication 1.2 is met. A medication order or a physical therapy episode is a treatment record. A statement of duration in the condition or the exam note is a duration record.

## 3. Exclusions

If any exclusion applies, the request is not covered. Exclusions override documentation in section 2.

### 3.1 Acute nonspecific low back pain (POL-LUMBAR-MRI-3.1)

Lumbar MRI is not covered for low back pain that has lasted less than six weeks when the record shows no neurologic deficit and no red flag from indication 1.2.

### 3.2 Axial pain without neurologic signs (POL-LUMBAR-MRI-3.2)

Lumbar MRI is not covered for low back pain without radicular symptoms and without a neurologic deficit, including when a normal neurologic exam is documented.

## Decision guide

Use the first matching row.

1. Any exclusion in section 3 applies: **not covered**.
2. No indication in section 1 is supported: **not covered**.
3. An indication in section 1 is supported and any applicable item in section 2 is missing: **missing information**.
4. An indication in section 1 is supported, no exclusion applies, and every applicable item in section 2 is present: **ready to submit**.
