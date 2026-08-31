# Building on SCORE: How CardioMet Lens Extends the South Asian Heart Center's Work

> *This document credits the SCORE tool as the conceptual origin of this
> project's approach. It does not describe any data-sharing, affiliation, or
> endorsement relationship, and none exists.*

## Credit where it's due

CardioMet Lens exists because of **SCORE**, the South Asian Heart Center's original
cardiometabolic comparison tool. SCORE pioneered the core idea this whole project
rests on: that a South Asian patient is best understood not against a generic
population, but against **peers like them** — matched on age, sex, ethnicity, and
medication use. SCORE put
that idea in front of patients first, established the clinical framing, and proved
there was genuine value in helping people see where their numbers stand before an
appointment. CardioMet Lens does not replace that insight; it builds directly on it.

## What CardioMet Lens inherits from SCORE

- **The premise:** compare a patient to a meaningful peer group, not a generic
  average.
- **The peer-matching capability:** benchmarking against people of the same sex,
  age band, and medication use.
- **The mission and tone:** educational, prevention-focused, culturally aware, and
  routed back to the clinician.

## Two reference populations, kept honestly distinct

The most important conceptual advance is how CardioMet Lens handles *who you are compared
against*. It offers **two clearly and separately labeled cohorts**, never blended:

1. *(Removed 2026-08-30.)* A second, South Asian-typed cohort shipped here. It
   was withdrawn because its provenance could not be established — see
   [`SAHC_COHORT.md`](SAHC_COHORT.md). What remains below describes the design
   intent, not a shipped comparison.
2. **NHANES Non-Hispanic Asian** — a public, reproducible U.S. survey population,
   honestly labeled as a *proxy* (NHANES has no South Asian–specific sample).

A patient or clinician can switch between them. Each carries its own truthful
label — the NHANES cohort is never called "South Asian" — so the comparison is
informative without overstating what the data represents. This is the line SCORE's
single blended filter didn't draw, and it matters for credibility.

## How it takes the idea further

CardioMet Lens keeps SCORE's strengths and improves on them, then adds layers SCORE
didn't have:

- **Peer matching, made trustworthy.** SCORE computed a percentile on whatever
  matched group resulted, however small. CardioMet Lens suppresses statistically
  unreliable small groups, falls back transparently to a broader peer set, and
  *discloses* the exact group used and its size.
- **Guideline-versioned classification.** Every threshold is traceable to a named
  guideline, lives in one source of truth, and is tested — replacing coarse,
  inlined bands.
- **South Asian–specific markers.** ApoB and Lp(a) — risk-enhancing factors that
  capture South Asian risk better than the standard panel — are added as
  guideline-classified context.
- **Trends over time.** Descriptive longitudinal tracking, with the patient owning
  their own data file (the server stores nothing).
- **A clinical handoff.** A discussion guide, a copy-ready pre-visit summary, and
  non-prescriptive next steps (family/cascade screening, prevention support).
- **Engineered safety.** Non-diagnostic by construction, with automated checks —
  so the tool can be extended without eroding its boundaries.

## The problems it solves — for patients and clinicians

**For patients:** a lab flag becomes a position. They see not just that a value is
off, but how far off relative to people genuinely like them, what guideline it
maps to, how it's trending, and what to ask — reducing both false alarm and false
reassurance, and arriving prepared.

**For clinicians:** a better-prepared patient and a focused, guideline-cited
summary that saves chart-prep time. The matched-peer view, advanced markers, and
South Asian context surface the right discussion points; every clinical decision
stays with the clinician, where it belongs.

## In one line

SCORE showed that South Asian patients deserve to be compared to the right peers.
CardioMet Lens takes that idea, makes the comparison honest and reliable across two
clearly distinct cohorts, and wraps it in the classification, tracking, and
clinical handoff that turn a single snapshot into something patients and
clinicians can actually act on.

> Educational only — not a diagnosis, prediction, or treatment recommendation.
> See [`PRODUCT_DESCRIPTION.md`](PRODUCT_DESCRIPTION.md) and
> [`SAHC_COHORT.md`](SAHC_COHORT.md) for detail.
