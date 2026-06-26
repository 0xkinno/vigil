"""Causality Assessment Service for Pharmacovigilance.

This module provides programmatic and command-line interfaces for assessing causality and seriousness
of Adverse Drug Event (ADE) reports.

It implements logic based on two primary international pharmacovigilance standards:
1. WHO-UMC Causality Assessment System:
   A simplified deterministic mapping of the WHO-UMC criteria using drug-event onset latency, dechallenge,
   rechallenge, and alternative cause evaluations to assign categories: Certain, Probable, Possible,
   Unlikely, Conditional, or Unassessable.
   
2. ICH Guideline E2D - Clinical Safety Data Management:
   Definitions and standards for expedited reporting, determining seriousness based on case outcome
   (death, life-threatening, hospitalization, disability, congenital-anomaly) and setting the standard
   reporting deadline (7, 15, or 90 days).
"""

import sys
import json
import os
from typing import Dict, Any, List

def assess(report: Dict[str, Any]) -> Dict[str, Any]:
    """Assess the causality, seriousness, and reporting deadline for an adverse drug event report.

    Args:
        report (dict): A dictionary containing the following keys:
            - suspectDrug (str): Name of the suspected medication.
            - adverseEvent (str): Name of the observed adverse effect.
            - onsetDaysAfterDrug (int): Days between starting the drug and event onset.
            - dechallenge (str): "positive", "negative", or "unknown".
            - rechallenge (str): "positive", "negative", or "none".
            - alternativeCause (bool): True if another plausible cause exists, False otherwise.
            - outcome (str): "death", "life-threatening", "hospitalization", "disability",
                             "congenital-anomaly", or "other".

    Returns:
        dict: A dictionary containing:
            - causality (str): "Certain", "Probable", "Possible", "Unlikely", "Conditional", or "Unassessable".
            - causalityReason (str): A brief, human-readable justification of the causality decision.
            - seriousness (str): "serious" or "non-serious".
            - reportingDeadlineDays (int): 7 (death/life-threatening), 15 (other serious), or 90 (non-serious).
    """
    # 1. Check for missing keys or None values
    required_keys = ["suspectDrug", "adverseEvent", "onsetDaysAfterDrug", "dechallenge", "rechallenge", "alternativeCause", "outcome"]
    missing_fields = [k for k in required_keys if k not in report or report[k] is None]
    
    # Extract outcome for seriousness calculation
    outcome = report.get("outcome")
    seriousness = "non-serious"
    reporting_deadline = 90
    
    valid_outcomes = {"death", "life-threatening", "hospitalization", "disability", "congenital-anomaly", "other"}
    
    # Calculate seriousness and deadline first where possible
    if outcome in valid_outcomes:
        if outcome in {"death", "life-threatening"}:
            seriousness = "serious"
            reporting_deadline = 7
        elif outcome in {"hospitalization", "disability", "congenital-anomaly"}:
            seriousness = "serious"
            reporting_deadline = 15
        else:
            seriousness = "non-serious"
            reporting_deadline = 90

    if missing_fields:
        return {
            "causality": "Unassessable",
            "causalityReason": f"Missing required input fields: {', '.join(missing_fields)}.",
            "seriousness": seriousness,
            "reportingDeadlineDays": reporting_deadline
        }

    # 2. Type and domain validation
    suspect_drug = report["suspectDrug"]
    adverse_event = report["adverseEvent"]
    onset_days = report["onsetDaysAfterDrug"]
    dechallenge = report["dechallenge"]
    rechallenge = report["rechallenge"]
    alternative_cause = report["alternativeCause"]
    
    invalid_reasons: List[str] = []
    if not isinstance(suspect_drug, str) or not suspect_drug.strip():
        invalid_reasons.append("suspectDrug must be a non-empty string")
    if not isinstance(adverse_event, str) or not adverse_event.strip():
        invalid_reasons.append("adverseEvent must be a non-empty string")
    if not isinstance(onset_days, int) and not (isinstance(onset_days, float) and onset_days.is_integer()):
        invalid_reasons.append("onsetDaysAfterDrug must be an integer")
    if dechallenge not in {"positive", "negative", "unknown"}:
        invalid_reasons.append("dechallenge must be 'positive', 'negative', or 'unknown'")
    if rechallenge not in {"positive", "negative", "none"}:
        invalid_reasons.append("rechallenge must be 'positive', 'negative', or 'none'")
    if not isinstance(alternative_cause, bool):
        invalid_reasons.append("alternativeCause must be a boolean")
    if outcome not in valid_outcomes:
        invalid_reasons.append("outcome must be one of: death, life-threatening, hospitalization, disability, congenital-anomaly, other")
        
    if invalid_reasons:
        return {
            "causality": "Unassessable",
            "causalityReason": f"Invalid input data: {'; '.join(invalid_reasons)}.",
            "seriousness": seriousness,
            "reportingDeadlineDays": reporting_deadline
        }

    # Normalize onset_days to int
    onset_days = int(onset_days)

    # 3. Check for obvious contradictions
    # If the adverse event did not stop when the drug was stopped (negative dechallenge),
    # it is contradictory to report that the event returned when the drug was re-given (positive rechallenge).
    if dechallenge == "negative" and rechallenge == "positive":
        return {
            "causality": "Unassessable",
            "causalityReason": "Contradictory data: positive rechallenge is reported despite a negative dechallenge.",
            "seriousness": seriousness,
            "reportingDeadlineDays": reporting_deadline
        }

    # 4. Assess Causality Category (WHO-UMC simplified logic)
    
    # Category: Unlikely
    # - Implausible time relationship (onset is negative, meaning event occurred before drug)
    # - OR strong alternative cause coupled with negative dechallenge (event persisted when drug stopped)
    if onset_days < 0:
        return {
            "causality": "Unlikely",
            "causalityReason": f"The event onset occurred {abs(onset_days)} days before drug administration, indicating an implausible time relationship.",
            "seriousness": seriousness,
            "reportingDeadlineDays": reporting_deadline
        }
    if alternative_cause is True and dechallenge == "negative":
        return {
            "causality": "Unlikely",
            "causalityReason": "A plausible alternative cause exists and the adverse event did not resolve upon drug withdrawal (negative dechallenge).",
            "seriousness": seriousness,
            "reportingDeadlineDays": reporting_deadline
        }

    # Category: Certain
    # - Plausible time relationship AND positive dechallenge AND positive rechallenge AND no alternative cause
    if dechallenge == "positive" and rechallenge == "positive" and alternative_cause is False:
        return {
            "causality": "Certain",
            "causalityReason": f"Plausible time to onset ({onset_days} days), positive dechallenge and rechallenge, and no alternative explanation exist.",
            "seriousness": seriousness,
            "reportingDeadlineDays": reporting_deadline
        }

    # Category: Probable
    # - Plausible time relationship AND positive dechallenge AND no alternative cause (rechallenge not positive)
    if dechallenge == "positive" and alternative_cause is False:
        return {
            "causality": "Probable",
            "causalityReason": f"Plausible time to onset ({onset_days} days), positive dechallenge, and no alternative explanation, without a positive rechallenge.",
            "seriousness": seriousness,
            "reportingDeadlineDays": reporting_deadline
        }

    # Category: Possible
    # - Plausible time relationship BUT alternative cause exists or dechallenge is unclear (unknown)
    if alternative_cause is True or dechallenge == "unknown":
        if alternative_cause is True and dechallenge == "unknown":
            reason = f"Plausible time to onset ({onset_days} days), but response to drug withdrawal is unclear and an alternative cause exists."
        elif alternative_cause is True:
            reason = f"Plausible time to onset ({onset_days} days), but a plausible alternative cause exists."
        else:
            reason = f"Plausible time to onset ({onset_days} days), but response to drug withdrawal (dechallenge) is unclear."
            
        return {
            "causality": "Possible",
            "causalityReason": reason,
            "seriousness": seriousness,
            "reportingDeadlineDays": reporting_deadline
        }

    # Category: Conditional
    # - Plausible time relationship, negative dechallenge, no alternative cause, rechallenge not positive.
    #   (The drug was stopped, the event persisted, but there is no alternative cause. Further data is required to judge).
    # - Other combinations of valid inputs that do not fit into the criteria above.
    return {
        "causality": "Conditional",
        "causalityReason": f"Plausible time to onset ({onset_days} days) with negative dechallenge and no alternative cause; further data are required to evaluate.",
        "seriousness": seriousness,
        "reportingDeadlineDays": reporting_deadline
    }

def run_self_tests() -> None:
    """Run internal test cases to verify logic accuracy."""
    print("Running self-tests for causality_service...")
    test_cases = [
        # 1. Certain (Plausible time, positive dechallenge, positive rechallenge, no alternative cause)
        (
            {
                "suspectDrug": "DrugA",
                "adverseEvent": "Rash",
                "onsetDaysAfterDrug": 3,
                "dechallenge": "positive",
                "rechallenge": "positive",
                "alternativeCause": False,
                "outcome": "other"
            },
            "Certain",
            "non-serious",
            90
        ),
        # 2. Probable (Plausible time, positive dechallenge, no alternative cause, rechallenge none)
        (
            {
                "suspectDrug": "DrugA",
                "adverseEvent": "Rash",
                "onsetDaysAfterDrug": 3,
                "dechallenge": "positive",
                "rechallenge": "none",
                "alternativeCause": False,
                "outcome": "hospitalization"
            },
            "Probable",
            "serious",
            15
        ),
        # 3. Possible (Plausible time, alternative cause exists)
        (
            {
                "suspectDrug": "DrugA",
                "adverseEvent": "Rash",
                "onsetDaysAfterDrug": 3,
                "dechallenge": "positive",
                "rechallenge": "none",
                "alternativeCause": True,
                "outcome": "other"
            },
            "Possible",
            "non-serious",
            90
        ),
        # 4. Possible (Plausible time, unclear dechallenge)
        (
            {
                "suspectDrug": "DrugA",
                "adverseEvent": "Rash",
                "onsetDaysAfterDrug": 3,
                "dechallenge": "unknown",
                "rechallenge": "none",
                "alternativeCause": False,
                "outcome": "other"
            },
            "Possible",
            "non-serious",
            90
        ),
        # 5. Unlikely (onsetDaysAfterDrug < 0)
        (
            {
                "suspectDrug": "DrugA",
                "adverseEvent": "Rash",
                "onsetDaysAfterDrug": -2,
                "dechallenge": "positive",
                "rechallenge": "none",
                "alternativeCause": False,
                "outcome": "other"
            },
            "Unlikely",
            "non-serious",
            90
        ),
        # 6. Unlikely (alternative cause + negative dechallenge)
        (
            {
                "suspectDrug": "DrugA",
                "adverseEvent": "Rash",
                "onsetDaysAfterDrug": 3,
                "dechallenge": "negative",
                "rechallenge": "none",
                "alternativeCause": True,
                "outcome": "other"
            },
            "Unlikely",
            "non-serious",
            90
        ),
        # 7. Conditional (dechallenge negative, no alternative cause, no positive rechallenge)
        (
            {
                "suspectDrug": "DrugA",
                "adverseEvent": "Rash",
                "onsetDaysAfterDrug": 3,
                "dechallenge": "negative",
                "rechallenge": "none",
                "alternativeCause": False,
                "outcome": "other"
            },
            "Conditional",
            "non-serious",
            90
        ),
        # 8. Unassessable (missing field)
        (
            {
                "suspectDrug": "DrugA",
                "adverseEvent": "Rash",
                "onsetDaysAfterDrug": None,
                "dechallenge": "positive",
                "rechallenge": "none",
                "alternativeCause": False,
                "outcome": "other"
            },
            "Unassessable",
            "non-serious",
            90
        ),
        # 9. Unassessable (contradictory dechallenge/rechallenge)
        (
            {
                "suspectDrug": "DrugA",
                "adverseEvent": "Rash",
                "onsetDaysAfterDrug": 3,
                "dechallenge": "negative",
                "rechallenge": "positive",
                "alternativeCause": False,
                "outcome": "other"
            },
            "Unassessable",
            "non-serious",
            90
        ),
        # 10. Seriousness / Deadline (death)
        (
            {
                "suspectDrug": "DrugA",
                "adverseEvent": "Anaphylaxis",
                "onsetDaysAfterDrug": 0,
                "dechallenge": "positive",
                "rechallenge": "none",
                "alternativeCause": False,
                "outcome": "death"
            },
            "Probable",
            "serious",
            7
        ),
    ]
    
    failures = 0
    for idx, (report, expected_causality, expected_seriousness, expected_deadline) in enumerate(test_cases):
        res = assess(report)
        c_ok = res["causality"] == expected_causality
        s_ok = res["seriousness"] == expected_seriousness
        d_ok = res["reportingDeadlineDays"] == expected_deadline
        
        if c_ok and s_ok and d_ok:
            continue
        
        failures += 1
        print(f"FAIL Test Case {idx + 1}: Report={report}")
        print(f"     Expected: causality={expected_causality}, seriousness={expected_seriousness}, deadline={expected_deadline}")
        print(f"     Got:      causality={res['causality']}, seriousness={res['seriousness']}, deadline={res['reportingDeadlineDays']}")
        print(f"     Reason:   {res.get('causalityReason')}")
            
    print(f"Self-tests complete: {len(test_cases) - failures}/{len(test_cases)} passed.")
    if failures > 0:
        sys.exit(1)

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python causality_service.py <path_to_json_file> [--self-test]", file=sys.stderr)
        sys.exit(1)
        
    file_path = sys.argv[1]
    
    if file_path == "--self-test":
        run_self_tests()
        sys.exit(0)
        
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
        
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            report = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in '{file_path}': {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}", file=sys.stderr)
        sys.exit(1)
        
    result = assess(report)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
