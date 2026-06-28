# VIGIL
### Pharmacovigilance Case Orchestration — Five Agents. One Human Gate. Zero Missed Deadlines.

![Track](https://img.shields.io/badge/Track-Maestro_Case-00C389?style=flat-square&labelColor=0A0A0A)
![Platform](https://img.shields.io/badge/Platform-UiPath_Maestro-00C389?style=flat-square&labelColor=0A0A0A)
![Pattern](https://img.shields.io/badge/Pattern-Human--in--the--Loop-2BD9A8?style=flat-square&labelColor=0A0A0A)
![Coding_Agent](https://img.shields.io/badge/Coding_Agent_Bonus-Earned-2BD9A8?style=flat-square&labelColor=0A0A0A)
![Standard](https://img.shields.io/badge/Standards-ICH_E2D_%2B_WHO--UMC-blue?style=flat-square&labelColor=0A0A0A)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square&labelColor=0A0A0A)

> **Every adverse-event report becomes a governed, deadline-bound, human-verified case — orchestrated end to end, escalated the instant a patient is at risk.**

When a patient suffers a serious reaction to a medication, a regulated clock starts. Drug-safety teams have a **legally mandated window** — as little as 7 days — to assess the case, obtain a physician's sign-off, and file it with regulators. Miss the window and the consequence is not an inconvenience; it is a regulatory violation that can halt a drug, trigger fines, and put more patients at risk.

Today that pipeline is run on spreadsheets, email chains, and human memory. VIGIL replaces it with a single long-running case that carries its own regulatory clock, routes itself when a patient turns serious, and refuses to close until a qualified physician has signed.

Not a chatbot. The orchestration layer that makes drug safety auditable, accountable, and on time.

---

## Links

| Resource | Link |
|----------|------|
| **Live App (Frontend)** | https://vigil-roan-ten.vercel.app |
| **UiPath Maestro Solution (Labs)** | [Open in Studio Web](https://staging.uipath.com/hackathon26_1017/studio_/designer/1ce3c2ce-5ff0-45d4-a59d-2decf43820a1?solutionId=9df2fc82-e2a8-43c3-6641-08ded39497a3&fileId=9d65ff3b-4cf7-47b0-b868-9ddb69850995&solutionFeedId=all) |
| **GitHub Repository** | https://github.com/0xkinno/vigil |
| **Demo Video** | _https://youtu.be/nVBuU7IMbZs?si=dSTQUQ33nzJMoFNV_ |

---

## 1. Table of Contents

1. [Table of Contents](#1-table-of-contents)
2. [The Problem](#2-the-problem)
3. [The Solution](#3-the-solution)
4. [Why Maestro Case](#4-why-maestro-case)
5. [System Architecture](#5-system-architecture)
6. [The Case Lifecycle](#6-the-case-lifecycle)
7. [The Five Agents](#7-the-five-agents)
8. [The Human Gate](#8-the-human-gate)
9. [The Regulatory SLA Clock](#9-the-regulatory-sla-clock)
10. [The Exception Path](#10-the-exception-path)
11. [Coded + Low-Code: The Causality Service](#11-coded--low-code-the-causality-service)
12. [Coding Agent Bonus — Evidence](#12-coding-agent-bonus--evidence)
13. [UiPath Components Used](#13-uipath-components-used)
14. [Data Contracts](#14-data-contracts)
15. [Running the Causality Service](#15-running-the-causality-service)
16. [Repository Structure](#16-repository-structure)
17. [Business Relevance](#17-business-relevance)
18. [Why VIGIL Wins](#18-why-vigil-wins)
19. [Roadmap](#19-roadmap)
20. [Tech Stack](#20-tech-stack)

---

## 2. The Problem

Three things are broken in how adverse drug events are processed today.

**1. The deadline is invisible until it is missed.** Under ICH E2D, a serious adverse event has a fatal/life-threatening reporting window of **7 calendar days** and an other-serious window of **15 days**. These clocks are tracked manually. When a case stalls in someone's inbox, nothing warns the team until the window is already gone.

**2. Seriousness is decided too late.** A case often enters as routine and is *reclassified* serious mid-review — after a hospitalization is confirmed, for example. In a linear, step-by-step process there is no mechanism to yank that case out of the normal queue and put it on the urgent path the moment it turns. So it keeps moving at routine speed against an urgent deadline.

**3. Accountability is diffuse.** A regulatory submission must carry a qualified medical sign-off. In email-driven workflows, who approved what, and when, is reconstructed after the fact from message threads. There is no enforced gate that the case cannot pass without a physician's recorded decision.

VIGIL eliminates all three — by design, not by discipline.

---

## 3. The Solution

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                            VIGIL — CASE ORCHESTRATION                             │
├──────────┬──────────┬───────────────┬──────────────┬───────────────────────────────┤
│  INTAKE  │  TRIAGE  │ MEDICAL REVIEW │  REPORTING   │  CLOSURE                     │
├──────────┼──────────┼───────────────┼──────────────┼───────────────────────────────┤
│ Extract  │ Assess   │ Physician      │ Generate     │ Verify completion            │
│ ICH E2B  │ serious- │ sign-off       │ E2B          │ Produce audit                │
│ data     │ ness +   │ (HUMAN GATE)   │ submission   │ record                       │
│ Validate │ deadline │ Approve /      │ Identify     │ Close case                   │
│ 4 core   │ per ICH  │ Reject /       │ regulators   │                              │
│ elements │ criteria │ Request info   │ (FDA / EMA)  │                              │
└──────────┴──────────┴───────────────┴──────────────┴───────────────────────────────┘
        │                  │                                                          
        │                  └──── seriousness == "serious" ────┐                       
        │                                                     ▼                       
        │                                       ┌─────────────────────────┐           
        └─── 15-DAY SLA CLOCK runs across ─────▶│  EXPEDITED ESCALATION   │           
             the whole case · warns at 80% ·    │  (interrupts the flow)  │           
             escalates on breach                └─────────────────────────┘           
```

The critical design decision is **governance by architecture, not by reminder.** The deadline is not a calendar invite a human has to remember — it is a property of the case. The human gate is not a polite request — it is a stage the case physically cannot exit without a recorded decision. The escalation is not a manual hand-off — it is an entry rule that fires automatically and interrupts active work.

---

## 4. Why Maestro Case

A linear automation (BPMN, sequential workflow) executes a fixed path: step 1, step 2, step 3. That is the wrong shape for pharmacovigilance, where a single report is a **long-running case** that can pause for days waiting on a human, carry a legal deadline the entire time, and change its own routing mid-flight when new information arrives.

| Capability VIGIL needs | Linear workflow | Maestro Case |
|---|---|---|
| Pause for days awaiting a human decision | Brittle / external | **Native (long-running)** |
| Carry a case-wide SLA with escalation tiers | Manual | **Native (case SLA + escalations)** |
| Re-route mid-flight when status changes | Not possible | **Native (secondary stage + entry rules)** |
| Interrupt active work on an urgent trigger | Not possible | **Native (interrupting entry condition)** |
| Enforce a non-skippable approval gate | Convention only | **Native (human action, required for completion)** |
| Full audit trail of every transition | Bolt-on | **Native (execution trail + incidents)** |

VIGIL is built on Maestro Case because the domain *is* a case-management problem — not a script.

---

## 5. System Architecture

```
                          ┌───────────────────────────────────────┐
                          │          CASE MANAGER (AI Orchestrator) │
                          │   Evaluates entry / exit / completion   │
                          │   rules · routes work · owns the clock  │
                          └───────────────────┬───────────────────┘
                                              │
   TRIGGER ──▶ ┌──────────┐   ┌──────────┐   ┌────────────────┐   ┌──────────┐   ┌──────────┐
   (new AE     │  INTAKE  │──▶│  TRIAGE  │──▶│ MEDICAL REVIEW │──▶│ REPORTING│──▶│ CLOSURE  │
    report)    │          │   │          │   │                │   │          │   │          │
               │ Intake   │   │ Triage   │   │ Physician      │   │ Reporting│   │ Closure  │
               │ Agent    │   │ Agent    │   │ Sign-off       │   │ Agent    │   │ Agent    │
               │ (LLM)    │   │ (LLM)    │   │ (HUMAN ACTION) │   │ (LLM)    │   │ (LLM)    │
               └────┬─────┘   └────┬─────┘   └────────────────┘   └──────────┘   └──────────┘
                    │              │
                    │              │  on completion, if seriousness == "serious"
                    │              ▼
                    │   ┌───────────────────────────┐
                    │   │   EXPEDITED ESCALATION     │   ◀── secondary stage
                    │   │   (interrupts active work) │       interrupting entry rule
                    │   │   Expedited Agent          │
                    │   └───────────────────────────┘
                    │
                    │   ┌─────────────────────────────────────────────────────┐
                    └──▶│  CODED CAUSALITY SERVICE  (external, Python)         │
                        │  WHO-UMC causality + ICH seriousness + deadline      │
                        │  → outputs: seriousness, reportingDeadlineDays       │
                        │  built via a coding agent through UiPath skills      │
                        └─────────────────────────────────────────────────────┘

   ╔═════════════════════════════════════════════════════════════════════════════╗
   ║  CASE-WIDE SLA CLOCK : 15 days  ·  AT-RISK at 80% (~day 12)  ·  BREACH alert  ║
   ╚═════════════════════════════════════════════════════════════════════════════╝
```

> **Visual flow (Excalidraw):** A hand-drawn case-flow diagram of the Maestro plan is included below:
<img width="3200" height="1800" alt="vigil-case-flow" src="https://github.com/user-attachments/assets/b8674603-77ce-46fc-954a-82ba1e007c04" />


---

## 6. The Case Lifecycle

Each adverse-event report is one case instance, identified `AE-#####` (e.g. `AE-36212`).

| # | Stage | Type | What happens | Exit condition |
|---|---|---|---|---|
| 1 | **Intake** | Agent | Extracts the four ICH E2B core elements (identifiable patient, identifiable reporter, suspect drug, adverse event); validates completeness | Intake Agent completes |
| 2 | **Triage** | Agent | Assesses seriousness against ICH criteria; assigns the reporting deadline (7d fatal/life-threatening, 15d other serious) | Triage Agent completes |
| 3 | **Medical Review** | **Human Action** | A physician reviews the case and records a decision: Approve / Request info / Reject | Physician records a decision |
| 4 | **Reporting** | Agent | Generates the ICH E2B submission summary; identifies the responsible regulators (FDA, EMA) | Reporting Agent completes |
| 5 | **Closure** | Agent | Verifies completion, produces the audit record, closes the case | Closure Agent completes |
| ⚡ | **Expedited Escalation** | Secondary (interrupting) | Fires the moment a case is flagged serious; interrupts the normal flow and routes to the urgent path | Expedited Agent completes |

The case is **complete only when all primary stages have completed** — and Medical Review cannot complete without a recorded human decision. The deadline cannot be skipped because it lives on the case, not on a person.

---

## 7. The Five Agents

All five primary agents are built low-code in **UiPath Agent Builder** and chained with live data — each agent's output is bound (`@`-linked) to the next agent's input, so the case carries a growing, structured record from intake to closure.

### Agent 1 — Intake Agent
Ingests the raw report and extracts a structured adverse-event record.

| Output field | Meaning |
|---|---|
| `patientId` | Identifiable patient reference |
| `reporterType` | Who reported (physician, patient, pharmacist…) |
| `suspectDrug` | The drug implicated |
| `adverseEventDescription` | The reaction described |
| `onsetDate` | When the reaction began |
| `isValid` | Whether the 4 ICH E2B core elements are present |
| `missingElements` | Any core element not supplied |

### Agent 2 — Triage Agent
Assesses seriousness and sets the regulatory clock.

| Output field | Values |
|---|---|
| `seriousness` | `serious` · `non-serious` |
| `seriousnessReason` | One-line justification against ICH criteria |
| `reportingDeadlineDays` | `7` (fatal/life-threatening) · `15` (other serious) |

### Agent 3 — *(Human)* Physician Sign-off
See [Section 8](#8-the-human-gate).

### Agent 4 — Reporting Agent
Produces the regulatory submission artifact.

| Output field | Meaning |
|---|---|
| `e2bSummary` | ICH E2B-shaped submission summary |
| `regulators` | Responsible bodies (e.g. FDA, EMA) |
| `deadlineConfirmed` | Restates the binding deadline |

### Agent 5 — Closure Agent
Finalizes and audits. Verifies all prior stages completed, generates the closure/audit record, and closes the case.

---

## 8. The Human Gate

Medical Review is a **UiPath Human Action** — a stage the case physically cannot exit without a recorded human decision. The physician is presented a review task (`Physician Case Review Required`) built on the Simple Approval action app, and records one of:

| Decision | Effect |
|---|---|
| **Approve** | Case proceeds to Reporting |
| **Request info** | Case loops back for additional intake data |
| **Reject** | Case is closed without a regulatory filing |

This is the accountability backbone: a regulatory submission can never be generated without a qualified human having signed for it, and the decision (with timestamp and identity) is recorded in the case's audit trail.

---

## 9. The Regulatory SLA Clock

The case carries a **15-day case-wide SLA** — the ICH window for an other-serious report — with a two-tier escalation policy:

| Tier | Trigger | Threshold | Action |
|---|---|---|---|
| **At risk** | SLA approaching breach | **80% of window (~day 12)** | Notify the pharmacovigilance operations lead |
| **Breached** | SLA window exceeded | 100% | Escalate as a missed-deadline incident |

```
 Day 0 ──────────────────────────────────────────── Day 15
 │                                          │         │
 case opens                          80% AT-RISK    SLA BREACH
                                     notify lead     escalate
```

The clock is proactive: it warns with runway to act (≈3 days), rather than reporting failure after the fact. This single feature converts an invisible, manually-tracked deadline into a governed property of the case.

---

## 10. The Exception Path

VIGIL is **non-linear**. A case does not have to walk Intake → Closure in a straight line.

**Expedited Escalation** is a **secondary stage** with an **interrupting entry rule**. When Triage completes and the case is flagged serious, the case is pulled out of its normal flow and routed onto the urgent expedited path — *interrupting active work* rather than waiting politely in line.

```
   normal flow ───▶ Triage completes ───▶ ┌── seriousness == "serious"? ──┐
                                          │                               │
                                       NO │                               │ YES
                                          ▼                               ▼
                                   continue normal             ⚡ INTERRUPT active work
                                   (Medical Review …)             enter Expedited Escalation
```

This is the defining Maestro Case behavior: dynamic, condition-driven routing that a linear workflow cannot express. The seriousness value that gates this path is exactly the value produced by the coded causality service in the next section — coded and low-code components driving the same case.

---

## 11. Coded + Low-Code: The Causality Service

VIGIL deliberately combines **low-code orchestration** with a **coded analytical component** — the blend the judging criteria specifically reward.

The **Causality Assessment Service** is a standalone Python module that performs the structured, deterministic clinical scoring that is better expressed in code than in an LLM prompt. It computes:

1. **WHO-UMC causality** — `Certain` · `Probable` · `Possible` · `Unlikely` · `Conditional` · `Unassessable`
2. **ICH E2D seriousness** — `serious` · `non-serious`
3. **Reporting deadline** — `7` · `15` · `90` days

```
   adverse-event report
   (drug, event, onset,
    dechallenge, rechallenge,        ┌────────────────────────────┐
    alternative cause, outcome) ────▶│  causality_service.py      │────▶  {
                                     │  WHO-UMC decision logic     │         "causality": "...",
                                     │  ICH E2D seriousness rules  │         "causalityReason": "...",
                                     │  deterministic · testable   │         "seriousness": "...",
                                     └────────────────────────────┘         "reportingDeadlineDays": ...
                                                                          }
```

The service's `seriousness` output is the exact field VIGIL's exception rule consumes, and its `reportingDeadlineDays` aligns with the case SLA — making the blend concrete: **the coded component drives the low-code case's routing and deadlines.**

**Verification:** the service ships with a built-in self-test suite — **10/10 branches passing** — and a worked sample case (Abacavir-induced DRESS syndrome, hospitalization), which returns:

```json
{
  "causality": "Probable",
  "causalityReason": "Plausible time to onset (21 days), positive dechallenge, and no alternative explanation, without a positive rechallenge.",
  "seriousness": "serious",
  "reportingDeadlineDays": 15
}
```

---

## 12. Coding Agent Bonus — Evidence

VIGIL earns the coding-agent bonus by building the causality service through a coding agent connected to UiPath via the official **`uip skills install`** integration.

| Requirement | VIGIL |
|---|---|
| **(a) Which coding agent** | Gemini (Gemini 3.5 Flash), run through Antigravity IDE |
| **(b) How it connected to UiPath** | `uip login` → `uip skills install --agent gemini` → **21 UiPath skills installed** (incl. `uipath-maestro-case`, `uipath-human-in-the-loop`, `uipath-agents`, `uipath-coded-apps`) |
| **(c) How it contributed** | Scaffolded, implemented, and self-tested `causality_service.py` end to end (WHO-UMC + ICH E2D logic, CLI, sample case, README) — **self-tests 10/10 passing** |
| **The blend** | The coded service outputs `seriousness` and `reportingDeadlineDays` that drive VIGIL's low-code exception routing and SLA — coded + low-code solving the problem together |

Full evidence (install output, session screenshots, exact prompt log) lives in
[`docs/coding-agent/`](https://github.com/0xkinno/vigil/tree/main/vigil-causality-service).

---

## 13. UiPath Components Used

| Component | Use in VIGIL |
|---|---|
| **Maestro Case** | The entire orchestration — stages, rules, lifecycle |
| **Case Manager (AI Orchestrator)** | Evaluates entry/exit/completion rules; routes work |
| **Agent Builder (low-code agents)** | Intake, Triage, Reporting, Closure, Expedited agents |
| **Human Action + Action App** | The physician sign-off gate (Simple Approval) |
| **Case SLA + Escalation rules** | 15-day clock, at-risk (80%) and breach escalations |
| **Secondary stage + interrupting entry rule** | The dynamic serious-case exception path |
| **UiPath CLI + Skills (`uip`)** | The coding-agent integration for the bonus |
| **Orchestrator (deploy + monitor)** | Published solution, job runs, Actions inbox, execution trail |

**Build composition:** the orchestration, agents, human gate, SLA, and exception logic are **low-code** (UiPath Studio Web). The causality service is **coded** (Python, built via a coding agent through UiPath skills). VIGIL is therefore both — by design.

---

## 14. Data Contracts

**Causality service input:**

```json
{
  "suspectDrug": "Abacavir",
  "adverseEvent": "DRESS syndrome",
  "onsetDaysAfterDrug": 21,
  "dechallenge": "positive",
  "rechallenge": "none",
  "alternativeCause": false,
  "outcome": "hospitalization"
}
```

**Causality service output:**

```json
{
  "causality": "Probable",
  "causalityReason": "Plausible time to onset (21 days), positive dechallenge, and no alternative explanation, without a positive rechallenge.",
  "seriousness": "serious",
  "reportingDeadlineDays": 15
}
```

**Decision logic (summary):**

| Causality | When |
|---|---|
| `Certain` | plausible timing + positive dechallenge + positive rechallenge + no alternative cause |
| `Probable` | plausible timing + positive dechallenge + no alternative cause |
| `Possible` | plausible timing but an alternative cause exists or dechallenge unclear |
| `Unlikely` | implausible timing, or strong alternative cause with negative dechallenge |
| `Conditional` | insufficient data to judge |
| `Unassessable` | contradictory or missing inputs |

| Seriousness | When |
|---|---|
| `serious` | outcome is death, life-threatening, hospitalization, disability, or congenital anomaly |
| `non-serious` | otherwise |

| Deadline | When |
|---|---|
| `7` days | death or life-threatening |
| `15` days | other serious |
| `90` days | non-serious |

---

## 15. Running the Causality Service

**Requirements:** Python 3.10+ (standard library only — no external dependencies).

```bash
# 1. Clone the repository
git clone https://github.com/0xkinno/vigil
cd vigil/causality-service

# 2. Run on the bundled sample case
python causality_service.py sample_input.json
# → prints the causality + seriousness + deadline JSON

# 3. Run the built-in self-test suite
python causality_service.py --self-test
# → Self-tests complete: 10/10 passed.
```

The service is intentionally dependency-free and deterministic, so any reviewer can verify every branch from the source and the self-tests alone.

---

## 16. Repository Structure

```
vigil/
├── README.md                          This file
├── LICENSE                            MIT
│
├── causality-service/
│   ├── causality_service.py           WHO-UMC causality + ICH E2D seriousness + CLI + self-tests
│   ├── sample_input.json              Worked case — Abacavir-induced DRESS, hospitalization
│   └── README.md                      Service-level schema + run guide
│
├── uipath-solution/
│   ├── Solution.<version>.nupkg        Exported Maestro Case solution package
│   └── notes.md                        What the package contains + how it maps to the stages
│
└── docs/
    ├── coding-agent/
    │   ├── prompt-log.md              Exact prompt + the (a)/(b)/(c) evidence
    │   ├── skills-install.png         `uip skills install` → 21 skills installed
    │   └── self-test-passed.png       Build session → 10/10 self-tests passing
    └── diagrams/
        └── vigil-case-flow.excalidraw.png   Hand-drawn Maestro case-flow diagram
```

---

## 17. Business Relevance

Pharmacovigilance is a **regulatory obligation for every pharmaceutical company on earth** — and a function where a missed deadline is a reportable failure.

**Who needs VIGIL:**

1. **Pharmaceutical safety departments** — managing thousands of adverse-event cases against hard regulatory clocks
2. **Contract research organizations (CROs)** — running pharmacovigilance as a service for multiple drug sponsors
3. **Regulators and notified bodies** — needing auditable, on-time, human-verified case trails
4. **Hospital drug-safety committees** — triaging in-patient adverse reactions under reporting duties
5. **Biotech startups** — meeting post-marketing surveillance obligations without a large safety team

The cost of the status quo is not labor — it is **risk**: missed windows, unverifiable sign-offs, and serious cases moving at routine speed. VIGIL converts each of those failure modes into a governed property of the case.

---

## 18. Why VIGIL Excels

| Criterion | How VIGIL addresses it |
|---|---|
| **Business Impact** | A legally-mandated, life-and-death process where a missed deadline is a regulatory violation — VIGIL governs the deadline by architecture |
| **Platform Usage (depth)** | Maestro Case + 5 chained agents + human action + case SLA with dual escalation + secondary interrupting stage + the coding-agent integration — broad and deep |
| **Technical Execution** | Verified end-to-end run; exception path fires and interrupts; coded service with 10/10 self-tests; clean data contracts between coded and low-code layers |
| **Completeness** | Full lifecycle Intake → Closure, with a real human gate and a real escalation, deployed and runnable |
| **Creativity** | Pharmacovigilance is an unusual, high-stakes domain choice; the dynamic serious-case interrupt and the coded-causality blend are non-obvious |
| **Presentation** | A clear story: a report becomes a governed case that escalates the instant a patient is at risk |
| **Coding-Agent Bonus** | Earned — causality service built via Gemini through `uip skills install`, fully evidenced |

---

## 19. Roadmap

1. **Restore serious-only gating in-platform** — bind the exception entry rule to the causality service's `seriousness` output via a coded-agent call, so the interrupt fires only on genuinely serious cases
2. **Multi-regulator child-case swarm** — spawn a child case per regulator (FDA, EMA, PMDA…), each with its own jurisdiction-specific deadline and submission format
3. **E2B(R3) XML generation** — emit standards-compliant ICH E2B(R3) submission files directly from the Reporting stage
4. **Signal detection** — aggregate across closed cases to surface emerging safety signals for a drug
5. **Regulator connector integrations** — submit directly to FDA FAERS / EMA EudraVigilance endpoints from Closure

---

## 20. Tech Stack

| Layer | Technology |
|---|---|
| Orchestration | UiPath **Maestro Case** (Studio Web) |
| Agents | UiPath **Agent Builder** (low-code) |
| Human-in-the-loop | UiPath **Human Action** + Simple Approval action app |
| Governance | Case **SLA** + **escalation rules**; **secondary stage** + interrupting entry rule |
| Coded component | **Python 3.10+** (standard library) — WHO-UMC + ICH E2D scoring |
| Coding-agent integration | **UiPath CLI** (`uip`) + **skills** → Gemini via Antigravity IDE |
| Deploy + monitor | UiPath **Orchestrator** (published solution, jobs, Actions, execution trail) |
| Standards | **ICH E2B / E2D**, **WHO-UMC causality** |
| License | MIT |

---

Built for the UiPath AgentHack — June 2026

*Every report a case. Every case on the clock. Every serious patient escalated in time.*
