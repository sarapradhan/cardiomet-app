# Technical Design — Trajectory Tracking, Phases T0–T1

> Design-before-code document. Defines the modules, data contracts, and algorithms that the TDD tests will pin down. Parent: `docs/trajectory/PRD_TRAJECTORY_T0_T1.md`.

## 1. Module layout
```
sahc_risklens/trajectory/
├── __init__.py
├── series.py        # T0: BiomarkerDraw, BiomarkerSeries, normalize/validate
├── health_file.py   # T0: portable export/import (dict <-> series), schema versioning
└── analytics.py     # T1: TrajectoryPoint, BiomarkerTrajectory, InterventionMarker, analyze_series()
```
Framework-free. Depends only on the standard library + the existing clinical core.

## 2. Data contracts (dataclasses)

### T0 — series.py
```python
@dataclass(frozen=True)
class BiomarkerDraw:
    draw_date: datetime.date
    values: dict          # the existing panel fields (LDL_mgdl, ..., medication flags)
    label: str | None = None

@dataclass(frozen=True)
class BiomarkerSeries:
    draws: tuple[BiomarkerDraw, ...]   # immutable, sorted ascending by draw_date
```
Functions:
- `make_series(draws: Iterable[BiomarkerDraw]) -> BiomarkerSeries` — validates (non-empty, no future dates), sorts ascending, returns immutable series.
- `SeriesValidationError(Exception)` — raised on empty series or future-dated draw.

### T0 — health_file.py
```python
SCHEMA_VERSION = "1.0"
def to_health_file(series: BiomarkerSeries) -> dict      # {schema_version, exported_at, series:{draws:[...]}}
def from_health_file(doc: dict) -> BiomarkerSeries        # validates schema_version; raises on unknown/old
class HealthFileError(Exception)
```
Round-trip invariant: `from_health_file(to_health_file(s))` equals `s` (dates as ISO strings in the doc, parsed back to `date`).

### T1 — analytics.py
```python
@dataclass(frozen=True)
class TrajectoryPoint:
    draw_date: date
    value: float | None
    category: str | None
    category_tone: str          # normal|elevated|high|missing (reuses categoryStyles logic, server-side copy)

@dataclass(frozen=True)
class CategoryTransition:
    from_category: str
    to_category: str
    from_date: date
    to_date: date

@dataclass(frozen=True)
class BiomarkerTrajectory:
    biomarker: str
    unit: str
    points: tuple[TrajectoryPoint, ...]
    direction: str              # improving|worsening|stable|insufficient_data
    change_absolute: float | None
    change_per_year: float | None
    transitions: tuple[CategoryTransition, ...]
    n_points: int

@dataclass(frozen=True)
class InterventionMarker:
    draw_date: date             # the draw at which the medication is first True
    change: str                 # e.g. "started cholesterol medication"
    affected_biomarkers: tuple[str, ...]
    observed_effects: tuple[str, ...]   # descriptive strings, one per affected biomarker present before & after

@dataclass(frozen=True)
class SeriesAnalysis:
    trajectories: tuple[BiomarkerTrajectory, ...]
    interventions: tuple[InterventionMarker, ...]

def analyze_series(series: BiomarkerSeries) -> SeriesAnalysis
```

## 3. Algorithms

### 3.1 Direction (per biomarker)
- Collect present `(date, value)` points, sorted.
- `n < 2` → `insufficient_data`.
- `delta = latest - earliest`. `good = delta if biomarker in HIGHER_IS_BETTER else -delta`.
- `abs(delta) < DEADBAND[biomarker]` → `stable`; `good > 0` → `improving`; else `worsening`.
- `HIGHER_IS_BETTER = {"HDL"}`. `DEADBAND` is a per-biomarker **display-noise** threshold (NOT clinical significance), documented inline.

### 3.2 Change
- `change_absolute = latest - earliest` (present points; None if `n < 2`).

### 3.3 Rate of change (per year)
- OLS slope of `value` vs `time_in_years` over present points; only if `n >= 2` and the dates span > 0 days; else None. Reported as an **observed historical rate** — never extrapolated.

### 3.4 Category transitions
- For each draw, category = `classify_all_biomarkers(draw.values)` → pick this biomarker's category.
- Walk consecutive draws; when both categories are non-None and differ, emit a `CategoryTransition`.

### 3.5 Interventions
- For each consecutive pair `(prev, cur)` and each medication flag in the canonical map, if flag is falsey in `prev` and truthy in `cur`: emit a marker dated at `cur.draw_date`.
- `affected_biomarkers` from the canonical medication→biomarker map (reused from the clinical core).
- `observed_effects`: for each affected biomarker present in both draws, a descriptive string: `"<BM> changed from <a> to <b> (<decreased|increased|no change> <|diff| unit>) by the next draw"`. No causal attribution.

## 4. Reuse & single-source-of-truth
- Per-point categories: `clinical.thresholds.classify_all_biomarkers`.
- Tone mapping: a server-side mirror of the frontend `categoryStyles` grouping, but to avoid drift it is derived from the same category names; documented as the one intentional duplication (frontend cannot import Python). Covered by a test that every category the classifier can emit maps to a known tone.
- Medication map & labels: exposed via **new additive public accessors** on the existing clinical modules (`medication_affects()`, `medication_labels()`) so the data is defined once. No underlying data changes; the 184-test suite must stay green.
- Units / biomarker labels: `clinical.biomarkers.BIOMARKERS`.

## 5. Safety design (NFR3) — descriptive, not predictive
Enforced by construction and by tests:
- No function emits a future date or a projected value.
- `direction` is a fixed enum; "worsening" describes the *number's* movement vs the preferred direction, not the person.
- Intervention strings state observation only ("changed from X to Y after the medication was started"), never causation ("the medication lowered…", "is working").
- No probability/percentage-risk output anywhere.
- A guardrail test scans every string field of `analyze_series` output against a forbidden-phrase list (`will reach`, `will develop`, `predict`, `expected to`, `is working`, `because of the`, `% risk`, etc.).

## 6. Test plan (TDD — written first)
- `tests/test_series.py`: construction, sort, empty rejection, future-date rejection, immutability, health-file round-trip, schema-version rejection.
- `tests/test_trajectory_analytics.py`: hand-computed direction (incl. HDL sense, stable deadband, insufficient_data), change_absolute, per-year slope, transitions (incl. the prediabetes→normal case), interventions (effect descriptive, correct affected set), and the guardrail scan.

## 7. Persona review gates (post-implementation)
- **Staff Engineer (Architecture)** — framework-free? contracts clean and typed? reuse correct?
- **Data & QA Auditor** — zero new thresholds? medication map reused? coverage adequate?
- **Clinical & Safety Reviewer** — descriptive-only? direction language neutral? interventions non-causal?
Each must record findings; Blockers fixed before T0–T1 is called done.
