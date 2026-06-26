# Coding Agent Evidence — VIGIL Causality Assessment Service

## (a) Which coding agent
Gemini (Gemini 3.5 Flash), run through Antigravity IDE, connected to the UiPath
platform via UiPath's official "UiPath for Coding Agents" integration.

## (b) How it was connected
Authenticated to the UiPath tenant and installed UiPath skills into the agent:
    uip login
    uip skills install --agent gemini
Result: 21 UiPath skills installed (Installed: 21), including uipath-maestro-case,
uipath-human-in-the-loop, uipath-agents, and uipath-coded-apps.

## (c) How it contributed
The agent scaffolded, implemented, and self-tested the causality-assessment
service end to end:
- causality_service.py — WHO-UMC causality logic + ICH E2D seriousness/deadline rules + CLI
- sample_input.json — realistic serious case (Abacavir-induced DRESS, hospitalization)
- README.md — schema + run guide
Verification: built-in self-tests 10/10 passed.
Sample output on the serious case:
    {
      "causality": "Probable",
      "causalityReason": "Plausible time to onset (21 days), positive dechallenge, and no alternative explanation, without a positive rechallenge.",
      "seriousness": "serious",
      "reportingDeadlineDays": 15
    }

## The blend (coded + low-code)
This coded service outputs the `seriousness` value and `reportingDeadlineDays`
that drive VIGIL's low-code Maestro Case: `seriousness` gates the Expedited
Escalation exception path, and `reportingDeadlineDays` (15) matches the case SLA
clock. Coded and low-code components solve the problem together.

## The exact prompt given to the agent

Build a Python service called "causality-assessment" for a pharmacovigilance system (adverse drug event safety).

PURPOSE: Given an adverse drug event report, compute two things:
1. WHO-UMC causality category: "Certain", "Probable", "Possible", "Unlikely", "Conditional", or "Unassessable"
2. ICH seriousness flag: "serious" or "non-serious"

INPUT (JSON): {
  "suspectDrug": str,
  "adverseEvent": str,
  "onsetDaysAfterDrug": int,        // days between drug start and event
  "dechallenge": "positive"|"negative"|"unknown",  // did event stop when drug stopped
  "rechallenge": "positive"|"negative"|"none",     // did event return when drug re-given
  "alternativeCause": bool,         // is there another plausible explanation
  "outcome": "death"|"life-threatening"|"hospitalization"|"disability"|"congenital-anomaly"|"other"
}

LOGIC:
- Causality (WHO-UMC simplified): 
  - "Certain" if plausible time relationship AND positive dechallenge AND positive rechallenge AND no alternative cause.
  - "Probable" if plausible time relationship AND positive dechallenge AND no alternative cause (rechallenge not required).
  - "Possible" if plausible time relationship BUT alternative cause exists or dechallenge unclear.
  - "Unlikely" if time relationship implausible (onsetDaysAfterDrug < 0) or strong alternative cause with negative dechallenge.
  - "Conditional" if data insufficient to judge.
  - "Unassessable" if inputs contradictory/missing.
- Seriousness (ICH E2D): "serious" if outcome is any of death, life-threatening, hospitalization, disability, congenital-anomaly; else "non-serious".

OUTPUT (JSON): {
  "causality": str,
  "causalityReason": str,        // one-sentence human-readable justification
  "seriousness": str,            // "serious" or "non-serious"
  "reportingDeadlineDays": int   // 7 if outcome death/life-threatening, 15 if other serious, 90 if non-serious
}

REQUIREMENTS:
- Single file: causality_service.py
- A function assess(report: dict) -> dict
- A CLI: `python causality_service.py sample_input.json` prints the JSON output
- Include a sample_input.json with a realistic serious case
- Include clear docstrings citing WHO-UMC and ICH E2D as the standards used
- No external dependencies beyond Python stdlib
- Add a short README.md explaining what it does and how to run it

Then run it on the sample input and show me the output.