/**
 * frontend/src/lib/types.ts
 * TypeScript mirror of api/models/patient.py and api/models/results.py.
 * SYNC RULE: When api/models/results.py changes, update this file in the same session.
 * Run `npm run type-check` after any change.
 */

export interface BiomarkerInput {
  LDL_mgdl?:  number | null;
  HDL_mgdl?:  number | null;
  TG_mgdl?:   number | null;
  TC_mgdl?:   number | null;
  FPG_mgdl?:  number | null;
  HbA1c_pct?: number | null;
  SBP_mmhg?:  number | null;
  DBP_mmhg?:  number | null;
  BMI_kgm2?:  number | null;
  age_yr?:      number | null;
  sex?:         'M' | 'F' | null;
  south_asian?: boolean | null;
  bp_med:   boolean;
  chol_med: boolean;
  insulin:  boolean;
  dm_pills: boolean;
}

export interface ThresholdResult {
  biomarker: string;
  value: number | null;
  unit: string;
  category: string | null;
  category_description: string;
  guideline_source: string;
  note: string | null;
}

export interface BenchmarkPoint {
  biomarker: string;
  patient_value: number | null;
  cohort_p10: number;
  cohort_p25: number;
  cohort_median: number;
  cohort_p75: number;
  cohort_p90: number;
  cohort_label: 'NHANES Non-Hispanic Asian';
  cohort_n: number;
}

export interface SouthAsianContextItem {
  factor: string;
  description: string;
  guideline_source: string;
}

export interface PhysicianGuideItem {
  biomarker: string;
  category: string;
  discussion_prompt: string;
  guideline_note: string;
}

export interface ThresholdCategory {
  category: string;
  range_description: string;
  guideline_source: string;
}

export interface BenchmarkResponse {
  threshold_results: ThresholdResult[];
  benchmark_data: BenchmarkPoint[];
  south_asian_context: SouthAsianContextItem[];
  physician_guide: PhysicianGuideItem[];
  missing_biomarkers: string[];
  medication_notes: string[];
  cohort_label: 'NHANES Non-Hispanic Asian';  // literal — always render exactly as received
  disclaimer: string;                          // always present — always render
  validation_status: string;
}

export interface ThresholdsResponse {
  LDL: ThresholdCategory[];
  HDL: ThresholdCategory[];
  TG: ThresholdCategory[];
  TC: ThresholdCategory[];
  HbA1c: ThresholdCategory[];
  FPG: ThresholdCategory[];
  SBP: ThresholdCategory[];
  DBP: ThresholdCategory[];
  BMI_standard: ThresholdCategory[];
  BMI_south_asian_context: ThresholdCategory[];
}

// --- Trajectory (longitudinal tracking) ---
// Mirror of api/models/series.py and api/models/trajectory.py.
// SYNC RULE: changing those Pydantic models requires updating these in the same change.

export interface BiomarkerDraw {
  draw_date: string;          // ISO date (YYYY-MM-DD)
  values: BiomarkerInput;
  label: string | null;
}

export interface BiomarkerSeries {
  draws: BiomarkerDraw[];
}

export interface TrajectoryPoint {
  draw_date: string;
  value: number | null;
  category: string | null;
  category_tone: 'normal' | 'elevated' | 'high' | 'missing';
}

export interface CategoryTransition {
  from_category: string;
  to_category: string;
  from_date: string;
  to_date: string;
}

export interface BiomarkerTrajectory {
  biomarker: string;
  unit: string;
  points: TrajectoryPoint[];
  direction: 'improving' | 'worsening' | 'stable' | 'insufficient_data';
  change_absolute: number | null;
  change_per_year: number | null;
  transitions: CategoryTransition[];
  n_points: number;
}

export interface InterventionMarker {
  draw_date: string;
  change: string;
  affected_biomarkers: string[];
  observed_effects: string[];
}

export interface TrajectoryResponse {
  trajectories: BiomarkerTrajectory[];
  interventions: InterventionMarker[];
  cohort_label: 'NHANES Non-Hispanic Asian';
  disclaimer: string;
  validation_status: string;
}
