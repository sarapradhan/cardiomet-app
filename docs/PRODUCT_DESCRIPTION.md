# SAHC RiskLens — Product Description

## In one paragraph

SAHC RiskLens is an educational, non-diagnostic web app that helps a person
understand their own cardiometabolic lab values — lipids, glucose, HbA1c, blood
pressure, body measures, and advanced lipids — against published clinical
guidelines and a population benchmark, with **South Asian risk context that
generic tools omit**. It classifies each value into a named guideline category,
shows where it sits within a chosen reference population (optionally matched to
the person's own age, sex, and medication use), tracks values over time, and
produces plain-language prompts and a clinician-ready summary to bring to an
appointment. It stores nothing on a server, diagnoses nothing, and recommends no
treatment. It is the safety-engineered successor to the South Asian Heart
Center's original **SCORE** comparison tool.

## The problem

A lab report tells a patient *that* a value is out of range, but rarely *how far*,
*relative to whom*, or *what's worth asking about*. The result is either
unwarranted alarm or false reassurance, and appointments spent re-explaining
basics. This is sharper for South Asians, who develop cardiometabolic disease
earlier and at lower BMI — a risk under-surfaced by generic tools and by standard
risk calculators.

## What it does

- **Explains each value** in a named guideline category (ACC/AHA, ADA, NCEP, WHO).
- **Benchmarks** the value against a reference population — choosing between a
  public proxy (NHANES Non-Hispanic Asian) and a genuine South Asian clinical
  cohort (South Asian Heart Center) — and can **match** the comparison group to
  the person's own sex, age range, and medication use.
- **Surfaces South Asian context** as guideline-recognized, qualitative risk-
  enhancing factors (ancestry; lower BMI action points; elevated Lp(a)).
- **Classifies advanced lipid markers** (ApoB, Lp(a)) that better capture South
  Asian risk than the standard panel.
- **Tracks trends over time** descriptively, with the history owned by the user.
- **Prepares the appointment** with a discussion guide, a copy-to-clipboard
  clinician pre-visit summary, and non-prescriptive next-step pointers (family/
  cascade screening, the center's prevention program).

## What it is not (and why that's a feature)

- **Not a diagnosis.** Output is descriptive ("LDL 168 is in the High category per
  ACC/AHA"), never "you have X".
- **Not a risk score or prediction.** A percentile is a position in a population,
  not a probability of an outcome.
- **Not treatment advice.** It routes decisions back to a clinician.
- **Not a data store.** No accounts, no server-side database; the person owns
  their longitudinal data as a portable file.

These boundaries are the product's design thesis and are enforced in code and
tests, not just stated in copy.

## Who it's for

- **The proactive patient** preparing for an appointment, who wants to understand
  their numbers in the right context.
- **The recently-flagged patient** who needs to know how concerning a value is and
  what to ask.
- **The reviewing clinician** (a stakeholder, not a user) who receives a focused,
  guideline-cited summary — and whose judgment gates clinical use.

## How it improves on SCORE

| | SCORE (original) | RiskLens |
|---|---|---|
| Form | Single Streamlit script | Three separated tiers (core / API / UI), tested |
| Cohorts | South Asian + NHANES mixed in one filter | Two clearly, honestly labeled cohorts you select |
| Peer matching | Yes, but on any cell size | Yes, with small-cell suppression + disclosure of the matched group |
| Thresholds | Coarse bands, inlined | Guideline-versioned, single source of truth, cited |
| Advanced lipids | — | ApoB, Lp(a) as risk-enhancing factors |
| Over time | Snapshot | Descriptive longitudinal trajectory |
| Clinician handoff | — | Pre-visit brief + care navigation |
| Data handling | Stored in committed databases | Stateless; user-owned health file |
| Safety | Standard disclaimer | Non-diagnostic by construction; automated scans; safety benchmark |

## Honest limitations

- The NHANES cohort is Non-Hispanic Asian (a proxy), labeled as such — not South
  Asian specific.
- The SAHC cohort's fasting glucose includes non-fasting draws (no fasting field
  in the extract), and its blood pressure is a single reading.
- ApoB/Lp(a) are classified against guideline cut-points but not population-
  benchmarked (the cohorts don't measure them); those thresholds are pending
  clinician sign-off.
- The highest-value longitudinal features (response-to-intervention, velocity)
  require a linked, date-stamped extract the de-identified data does not yet
  provide.

## Status

Phase 1 — educational demonstration. Production use is gated on documented
clinician review, a regulatory (non-device clinical decision support)
determination, a privacy policy, security hardening, and an accessibility audit.
See [`PHASE2_ROADMAP.md`](PHASE2_ROADMAP.md). For the deeper persona and
user-story treatment, see [`PRODUCT_OVERVIEW.md`](PRODUCT_OVERVIEW.md).
