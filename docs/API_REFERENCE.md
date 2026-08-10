# CardioMet Lens — API Reference

Base path: the FastAPI app serves `GET /health` at the root and the versioned API
under `/api/v1`. Interactive docs are available at `/docs` (Swagger) and
`/redoc` when the server is running. All endpoints are `GET` or `POST`; CORS
origins come from `ALLOWED_ORIGINS`.

The authoritative schema lives in `api/models/` (Pydantic) and is mirrored in
`frontend/src/lib/types.ts`. This page documents the current contract.

---

## POST `/api/v1/benchmark`

Classify and benchmark a single panel of values.

### Query parameters

| Param | Type | Default | Notes |
|---|---|---|---|
| `cohort` | `nhanes_asian` \| `sahc` | `nhanes_asian` | Reference cohort. Unknown value → `422`. |
| `match` | boolean | `false` | Benchmark against the patient's matched peer subgroup (sex + age band + medication). Requires `sex` and `age_yr`; offered for the SAHC cohort (NHANES falls back to whole-cohort with `matched=false`). |

### Request body — `BiomarkerInput`

All clinical fields are optional (blank → reported as not provided). Ranges are
validated; out-of-range → `422`.

| Field | Type | Range | Unit |
|---|---|---|---|
| `LDL_mgdl` | float? | 0–500 | mg/dL |
| `HDL_mgdl` | float? | 0–200 | mg/dL |
| `TG_mgdl` | float? | 0–5000 | mg/dL |
| `TC_mgdl` | float? | 0–700 | mg/dL |
| `FPG_mgdl` | float? | 0–1000 | mg/dL |
| `fasting_status` | `"confirmed" \| "not_fasting" \| "unknown"`? | — | FPG is only classified against fasting-glucose categories when this is exactly `"confirmed"`. Omitted/`null`/`"unknown"`/`"not_fasting"` all suppress FPG classification (`category: null`, with an explanatory `category_description`) — see `docs/CLINICAL_LOGIC_APPENDIX.md`. |
| `fasting_hours` | float? | 0–72 | Informational only; does not itself confirm fasting status. |
| `HbA1c_pct` | float? | 0–20 | % |
| `SBP_mmhg` | float? | 0–300 | mm Hg |
| `DBP_mmhg` | float? | 0–200 | mm Hg |
| `BMI_kgm2` | float? | 10–80 | kg/m² |
| `ApoB_mgdl` | float? | 0–300 | mg/dL (classification-only) |
| `Lpa_mgdl` | float? | 0–500 | mg/dL (classification-only) |
| `age_yr` | int? | 18–120 | years |
| `sex` | `"M"` \| `"F"` \| null | — | for HDL thresholds + matching |
| `south_asian` | bool? | — | gates the South Asian context |
| `chol_med`, `bp_med`, `insulin`, `dm_pills` | bool | default false | medication flags |

### Response — `BenchmarkResponse`

| Field | Type | Notes |
|---|---|---|
| `threshold_results` | `ThresholdResult[]` | the 9 core biomarkers, classified |
| `risk_enhancing_markers` | `ThresholdResult[]` | ApoB/Lp(a), present only if supplied; classification-only |
| `benchmark_data` | `BenchmarkPoint[]` | per-biomarker reference distribution + patient value |
| `south_asian_context` | `SouthAsianContextItem[]` | present when `south_asian` (and for elevated Lp(a)) |
| `physician_guide` | `PhysicianGuideItem[]` | template prompts for non-normal values |
| `care_navigation` | `CareNavigationItem[]` | family/cascade screening, prevention pointer |
| `missing_biomarkers` | `string[]` | input field names left blank (core 9 only) |
| `medication_notes` | `string[]` | medication caveats |
| `cohort` | `string` | selected cohort id |
| `cohort_label` | `"NHANES Non-Hispanic Asian"` \| `"South Asian Heart Center clinical cohort"` | honest label |
| `matched` | bool | true if peer matching applied to ≥1 biomarker |
| `match_description` | string? | peer group used, e.g. "Women, 49–64" |
| `disclaimer` | string | always present, always rendered |
| `validation_status` | string | e.g. "Phase 1 — Demo" |

`ThresholdResult`: `biomarker, value, unit, category, category_description,
guideline_source, note`.

`BenchmarkPoint`: `biomarker, patient_value, cohort_p10, cohort_p25,
cohort_median, cohort_p75, cohort_p90, cohort_label, cohort_n, matched, match_n,
match_description`.

### Examples

```bash
# Default: NHANES cohort, no matching
curl -s -X POST localhost:8000/api/v1/benchmark \
  -H 'Content-Type: application/json' \
  -d '{"LDL_mgdl":142,"HDL_mgdl":40,"south_asian":true}'

# SAHC cohort + peer matching + advanced markers
curl -s -X POST 'localhost:8000/api/v1/benchmark?cohort=sahc&match=true' \
  -H 'Content-Type: application/json' \
  -d '{"LDL_mgdl":150,"HDL_mgdl":42,"ApoB_mgdl":135,"Lpa_mgdl":60,
       "age_yr":55,"sex":"F","south_asian":true,"chol_med":true,"BMI_kgm2":27}'
```

---

## POST `/api/v1/trajectory`

Descriptive trend analysis over a dated series. Stateless — the server stores
nothing.

### Request body — `BiomarkerSeriesIn`

```jsonc
{
  "draws": [
    { "draw_date": "2025-01-10", "values": { /* BiomarkerInput */ }, "label": "baseline" },
    { "draw_date": "2025-07-02", "values": { /* BiomarkerInput */ }, "label": "after statin" }
  ]
}
```

At least one draw; `draw_date` is ISO `YYYY-MM-DD`; future dates are rejected.

### Response — `TrajectoryResponse`

`trajectories` (per-biomarker points, direction, absolute/per-year change,
category transitions), `interventions` (medication-change markers with observed
effects), `cohort_label`, `disclaimer`, `validation_status`. Strictly
descriptive — no forecasting, no causal attribution, no risk score.

---

## GET `/api/v1/thresholds`

Returns the full guideline reference table — `ThresholdsResponse` with
`LDL, HDL, TG, TC, HbA1c, FPG, SBP, DBP, BMI_standard, BMI_south_asian_context`,
each a list of `{category, range_description, guideline_source}`. HDL entries are
suffixed `(Male)` / `(Female)`.

---

## GET `/health`

`{ "status": "ok", "version": "...", "nhanes_loaded": bool, "mode": "live"|"demo" }`

---

## Errors

- `422 Unprocessable Entity` — input validation failure (out-of-range value, bad
  `sex`, unknown `cohort`, future draw date).
- `4xx/5xx` bodies follow FastAPI's `{ "detail": ... }` convention.
