# Causality Assessment Service

A Python safety tool for pharmacovigilance (adverse drug event safety) designed to assess causality and seriousness of adverse event reports.

This service utilizes two major international pharmacovigilance standards:
- **WHO-UMC Causality Assessment System**: Simplifies causality categories based on chronological relationship, dechallenge/rechallenge events, and potential alternative explanations.
- **ICH Guideline E2D (Clinical Safety Data Management)**: Classifies case seriousness and sets reporting deadlines (7, 15, or 90 days) based on clinical outcomes.

---

## Architecture: Coded + Low-Code

VIGIL combines low-code and coded components. The Maestro Case orchestration
(5-stage case, agents, 15-day SLA clock with at-risk + breach escalations,
interrupting exception stage, and human physician sign-off) is built low-code in
UiPath Studio Web. The causality-assessment service is a coded Python component,
built using a coding agent (Gemini via Antigravity IDE) connected through
UiPath's `uip skills install` integration. This coded service computes WHO-UMC
causality and outputs the `seriousness` value and `reportingDeadlineDays` that
drive VIGIL's exception routing and SLA deadlines — demonstrating coded and
low-code components solving the problem together.

---

## Input JSON Schema

The tool expects a JSON file with the following structure:

```json
{
  "suspectDrug": "Abacavir",
  "adverseEvent": "Drug Reaction with Eosinophilia and Systemic Symptoms (DRESS)",
  "onsetDaysAfterDrug": 21,
  "dechallenge": "positive",
  "rechallenge": "none",
  "alternativeCause": false,
  "outcome": "hospitalization"
}
```

### Parameter Values
- **`onsetDaysAfterDrug`** (`int`): Days between starting the drug and event onset.
- **`dechallenge`** (`str`): `"positive"`, `"negative"`, or `"unknown"`.
- **`rechallenge`** (`str`): `"positive"`, `"negative"`, or `"none"`.
- **`alternativeCause`** (`bool`): `true` if another plausible explanation exists, `false` otherwise.
- **`outcome`** (`str`): `"death"`, `"life-threatening"`, `"hospitalization"`, `"disability"`, `"congenital-anomaly"`, or `"other"`.

---

## Output JSON Schema

The tool outputs a pretty-printed JSON response:

```json
{
  "causality": "Probable",
  "causalityReason": "Plausible time to onset (21 days), positive dechallenge, and no alternative explanation, without a positive rechallenge.",
  "seriousness": "serious",
  "reportingDeadlineDays": 15
}
```

### Response Fields
- **`causality`** (`str`): One of `"Certain"`, `"Probable"`, `"Possible"`, `"Unlikely"`, `"Conditional"`, or `"Unassessable"`.
- **`causalityReason`** (`str`): A one-sentence, human-readable justification of the causality decision.
- **`seriousness`** (`str`): `"serious"` or `"non-serious"`.
- **`reportingDeadlineDays`** (`int`):
  - `7`: Serious event with outcome `death` or `life-threatening`.
  - `15`: Serious event with outcome `hospitalization`, `disability`, or `congenital-anomaly`.
  - `90`: Non-serious event (outcome `other`).

---

## Rules and Logic

### 1. Seriousness (ICH E2D)
An event is classified as **serious** if the outcome is any of: `death`, `life-threatening`, `hospitalization`, `disability`, or `congenital-anomaly`. Otherwise, it is **non-serious**.

### 2. Reporting Deadline (ICH E2D)
- **7 Days**: Serious event with outcome `death` or `life-threatening`.
- **15 Days**: Serious event with other outcomes.
- **90 Days**: Non-serious event.

### 3. Causality (WHO-UMC Simplified)
- **Unassessable**: If required fields are missing, invalid, or contradictory (e.g., reporting a positive rechallenge despite a negative dechallenge).
- **Unlikely**: If onset occurs before drug administration (`onsetDaysAfterDrug < 0`) OR if a strong alternative cause exists and dechallenge is negative.
- **Certain**: If onset is plausible (`>= 0`), dechallenge is positive, rechallenge is positive, and no alternative cause exists.
- **Probable**: If onset is plausible (`>= 0`), dechallenge is positive, no alternative cause exists, and rechallenge is not positive.
- **Possible**: If onset is plausible (`>= 0`), but an alternative cause exists OR the dechallenge is unclear (`unknown`).
- **Conditional**: If onset is plausible (`>= 0`), dechallenge is negative, no alternative cause exists, and rechallenge is not positive (representing a case where the event persisted after drug withdrawal but no other cause explains it; hence, more data is needed).

---

## How to Run

No external dependencies beyond the Python Standard Library are required.

### 1. As a CLI Tool
To process a report JSON file:
```bash
python causality_service.py sample_input.json
```

### 2. Run Self-Tests
To execute built-in unit test scenarios:
```bash
python causality_service.py --self-test
```

### 3. As a Python Library
You can import the `assess` function inside your own Python modules:
```python
from causality_service import assess

report = {
    "suspectDrug": "Aspirin",
    "adverseEvent": "Gastrointestinal Bleeding",
    "onsetDaysAfterDrug": 5,
    "dechallenge": "positive",
    "rechallenge": "none",
    "alternativeCause": False,
    "outcome": "hospitalization"
}

result = assess(report)
print(result)
```
