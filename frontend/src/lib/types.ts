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
