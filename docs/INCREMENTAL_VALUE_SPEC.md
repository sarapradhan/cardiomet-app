# SAHC RiskLens — Incremental Value Specification
## Longitudinal Trajectory Tracking ("RiskLens Timeline")

> **The strategic problem this solves:** a savvy patient with a general-purpose AI assistant can already get a one-time interpretation of a single lab panel. A single-snapshot tool is therefore commoditized. This document specifies the capability that is structurally hard for a stateless chat session to replicate — and that is also the most clinically meaningful: tracking cardiometabolic values *over time*.

---

## 1. The differentiation thesis (read this first)

### What a chatbot already does well
Given one set of lab values, a general AI assistant can classify them against guidelines, explain them in plain language, and suggest questions. Our single-draw `/benchmark` flow is, candidly, a structured version of this. We should not pretend otherwise, and we should not compete on it.

### What a chatbot does badly — and where we win
A chat session is **stateless and unverifiable**. It does not hold your December draw, your May draw, and the one before; it cannot compute the *velocity* of your ApoB across them; it cannot tell you the statin moved your LDL less than expected; and a patient cannot confirm it didn't quote a superseded threshold. Four durable advantages follow:

1. **Trajectory over snapshot.** The clinical signal in cardiometabolic health is largely in the *trend* — rate of change, response to intervention, and time-to-threshold — none of which exist in a single panel.
2. **Verifiable, versioned clinical logic.** Every threshold is traceable to a named guideline, covered by tests, and reviewable by a clinician. "Verified" beats "a model said so."
3. **Real population calibration.** We compute actual NHANES Non-Hispanic Asian percentiles from the source data; a chatbot approximates "typical" ranges from memory.
4. **A structured artifact for the clinical encounter.** The output is a dated, guideline-cited summary a clinician can act on in minutes — a workflow benefit, not just an information one.

### Why this matters more for the target population
South Asians develop cardiometabolic disease **earlier and at lower BMI**. Early detection of an adverse *trajectory* — a creeping HbA1c, a rising ApoB — is therefore higher-value here than in the populations generic tools are tuned to. Trajectory tracking is not a generic feature bolted on; it is the feature most aligned with the mission.

---

## 2. The hard constraint we must preserve: privacy

Phase 1's defining property is that **nothing is stored server-side** — which is what keeps the privacy and regulatory surface minimal. Longitudinal tracking appears to require persistence, creating a real tension. We resolve it deliberately:

**Decision: the patient owns their data. The server stays stateless.**

We support longitudinal tracking *without a server-side database* via two mechanisms:

- **In-session, multi-draw entry** — the user enters or uploads several dated draws at once and gets a trajectory analysis in that session.
- **A user-owned "health file"** — the app can export the user's draw history as a single portable JSON file they save themselves, and re-import it later to continue tracking. The browser may also cache it locally (the user's own device) for convenience, with an explicit clear control.

This preserves the "we store nothing" claim — the strongest trust and regulatory property of the product — while delivering the longitudinal value. It is also a *better* privacy story than competitors who silently warehouse health data, and it is itself a differentiator worth stating out loud.

> Server-side accounts and storage are explicitly **out of scope** for this capability and deferred to a future phase that would require the full HIPAA/security treatment in `PHASE2_ROADMAP.md`. We are choosing the architecture that keeps the regulatory gate low.

---

## 3. Scope

### In scope
- A draw is a single dated panel (the existing `BiomarkerInput` plus a `draw_date`).
- A series is an ordered set of draws for one person.
- Per-biomarker time series with category bands.
- Descriptive trajectory analytics: direction, rate of change, change vs. prior draw, category transitions over time.
- Response-to-intervention annotation: when a medication flag changes between draws, mark it on the timeline and report the observed change in the affected biomarkers.
- Export/import of a user-owned health file (portable JSON).
- A timeline visualization (small multiples / sparklines with category bands and intervention markers).

### Explicitly out of scope (and why)
- **Server-side storage / accounts** — preserves statelessness; deferred to a later, gated phase.
- **Predictive modeling / individual risk forecasting** — would cross from education into a regulated medical-device claim, and into the "overclaiming" we are avoiding. We describe the past; we do not predict the future (see §6).
- **Automated clinical alerts / nudges** — anything that pushes a user to act is advice, not education.

---

## 4. Data model

### 4.1 New: a dated draw
Extends the existing single-draw input with a date. The existing `BiomarkerInput` is unchanged; we wrap it.

```
BiomarkerDraw:
    draw_date: date              # ISO date of the lab draw (required)
    values: BiomarkerInput       # the existing 16-field panel
    label: str | None            # optional user note, e.g. "after starting statin"
```

### 4.2 New: a series
```
BiomarkerSeries:
    draws: list[BiomarkerDraw]   # 1..N, sorted ascending by draw_date on ingest
    schema_version: str          # for forward-compatible health-file import
```

### 4.3 The user-owned health file
A single JSON document the user exports and re-imports. It IS a `BiomarkerSeries` plus minimal metadata:
```
HealthFile:
    schema_version: "1.0"
    exported_at: <timestamp>
    series: BiomarkerSeries
```
No identifiers, no account, no PII beyond the biomarker values the user themselves entered. The user controls the file entirely.

### 4.4 Trajectory output (new response model)
Per biomarker, computed across the series:
```
TrajectoryPoint:        # one per draw, per biomarker
    draw_date: date
    value: float | None
    category: str | None        # reuses the existing classification engine
    category_tone: str          # normal/elevated/high/missing (existing helper)

BiomarkerTrajectory:
    biomarker: str
    unit: str
    points: list[TrajectoryPoint]
    direction: "improving" | "worsening" | "stable" | "insufficient_data"
    change_absolute: float | None      # latest minus earliest (present values)
    change_per_year: float | None      # slope, only if >= 2 dated points span time
    category_transitions: list[...]    # e.g. "Prediabetes -> Normal between 2025-12 and 2026-05"
    n_points: int

InterventionMarker:
    draw_date: date
    change: str                 # e.g. "started cholesterol medication"
    affected_biomarkers: list[str]
    observed_effect: str        # descriptive only, e.g. "LDL decreased 38 mg/dL over the next draw"

TrajectoryResponse:
    trajectories: list[BiomarkerTrajectory]
    interventions: list[InterventionMarker]
    cohort_label: Literal["NHANES Non-Hispanic Asian"]
    disclaimer: str
    validation_status: str
```

The trajectory engine **reuses** the existing `classify_all_biomarkers` for per-point categories, so the single source of truth for thresholds is unchanged — longitudinal logic sits on top of, never duplicates, the clinical core.

---

## 5. The analytics, precisely defined

Each is deliberately **descriptive**, computed with transparent arithmetic (no opaque model), and explainable to a clinician.

**Direction.** Compare the earliest and latest present value, accounting for whether higher is better (HDL) or worse (LDL, HbA1c, etc.). Map to improving / worsening / stable, with a stability deadband (e.g. change under a small per-biomarker threshold = "stable"). "insufficient_data" when fewer than two present values.

**Change vs. prior.** The simple delta between consecutive draws — the number a patient most intuitively wants ("my LDL dropped 38").

**Rate of change (per year).** Ordinary least-squares slope of value vs. time, reported per year, only when ≥2 dated points span a non-trivial interval. Presented as an observed historical rate, never extrapolated forward (see §6).

**Category transitions.** Using the existing classifier per draw, detect when the category changed and between which dates ("Prediabetes → Normal between Dec 2025 and May 2026"). This is the most clinically legible output and maps directly to guideline language.

**Response-to-intervention.** When a medication flag flips from false to true between consecutive draws, emit an `InterventionMarker` and report the observed change in the biomarkers that medication class affects (reusing the existing `_MED_AFFECTS` mapping). Strictly descriptive: "after the cholesterol medication was started, LDL decreased 38 mg/dL by the next draw." Never "the medication is working" (a clinical judgment).

---

## 6. Clinical safety for trajectories (critical)

Longitudinal features make it easy to slip from education into prediction or advice. Guardrails, enforced in code and tests:

- **No forward projection of individual values.** We never say "your HbA1c will reach 6.5 by 2027." Time-to-threshold language is forbidden. We report only what has already been observed. (A test asserts no future-dated projections appear in output.)
- **No causal claims about interventions.** "LDL decreased after the statin started" is allowed (observation); "the statin lowered your LDL" / "the statin is working" is not (attribution/judgment).
- **No risk scores or probabilities**, consistent with the rest of the product.
- **Direction language stays neutral.** "Worsening" describes the number's movement relative to the guideline-preferred direction; it is not a statement about the person's health or prognosis. Copy is reviewed to avoid alarm.
- **Disclaimer and limitations persist** on every trajectory view, including a new limitation: *a small number of draws can be misleading; lab values fluctuate for many reasons; trends are discussion context, not conclusions.*
- **All trajectory output routes back to the clinician** via the same physician-discussion framing.

These guardrails are part of the Clinical & Safety Reviewer's checklist for this feature and must pass before release.

---

## 7. User experience

**Entry.** Two paths: (a) add draws one at a time across a session, each with a date; (b) import a previously exported health file. A returning user with a cached local file lands directly on their timeline.

**The timeline view.** The hero of the feature. Per biomarker, a compact sparkline over time with the guideline category bands shaded behind it, the patient's points plotted, and intervention markers (e.g. a small flag where medication started). Small multiples so the whole cardiometabolic picture is visible at once. Tapping a biomarker expands it to the full distribution-plus-history view.

**The trajectory summary.** Plain-language, per biomarker: "LDL: 162 → 124 over 5 months (improving). Crossed from High to Near Optimal. Cholesterol medication started before the latest draw." Plus the same always-on disclaimer and limitations.

**Export.** A one-tap "save my health file" that downloads the portable JSON, with copy explaining the user owns it and we keep nothing.

**Design.** Reuses the existing Material Design 3 tokens and the `categoryStyles` chip tones; the timeline is the one genuinely new component.

---

## 8. Architecture fit

This layers cleanly onto the existing three-tier design:

- **Clinical core (`sahc_risklens/`)** — a new `sahc_risklens/trajectory/` package: `series.py` (validation, sorting, dedupe by date), `analytics.py` (direction, slope, transitions, interventions). Reuses `clinical/thresholds.py` and `clinical/biomarkers.py` unchanged. No new clinical thresholds are introduced.
- **API (`api/`)** — a new `POST /api/v1/trajectory` endpoint taking a `BiomarkerSeries`, returning a `TrajectoryResponse`. Thin, like the existing routers. New models in `api/models/`. The server remains stateless — it computes on the posted series and returns; it stores nothing.
- **Frontend (`frontend/`)** — a new timeline route and `Timeline` / `TrajectorySummary` components; export/import via the File API and (optional) local browser cache; `types.ts` extended to mirror the new models. No clinical logic in the browser.
- **Tests** — new unit suites for series handling and analytics (including the safety guardrails), an integration suite for the endpoint, and an e2e check. Held to the same single-source-of-truth and validation-gate standards.

---

## 9. How this strengthens the differentiation, concretely

After this capability ships, the honest pitch changes from "interpret my labs" (commoditized) to:

> *A longitudinal, verifiable, population-calibrated cardiometabolic tracker for an under-served high-risk group — that you own and we never store.*

Each clause is something a chat session cannot match: longitudinal (stateful over time), verifiable (tested, guideline-traceable), population-calibrated (real NHANES percentiles), under-served group (South Asian focus), user-owned (privacy as a feature). That is a defensible position rather than a wrapper around a commodity.

---

## 10. Honest assessment of remaining commoditization risk

Worth stating plainly so it's designed around rather than discovered later: a sufficiently determined user could still paste multiple draws into a chatbot and ask for a trend. What they *cannot* easily get is the combination of (a) verified, versioned thresholds, (b) real computed population percentiles, (c) a consistent dated artifact they can hand a clinician, and (d) a privacy guarantee. The moat is the *combination and the rigor*, not any single feature. The product should be marketed and built accordingly — and should keep raising the rigor bar (clinician review, guideline-version tracking, expanding the verified biomarker set) as the durable advantage.
