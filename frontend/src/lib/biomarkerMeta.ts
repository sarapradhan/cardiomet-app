/**
 * frontend/src/lib/biomarkerMeta.ts
 * Maps each biomarker to a clinical group, for the color-coded legend that
 * threads through cards, charts, and the timeline. Group hues are defined in
 * globals.css (--grp-*). Presentation only — never affects classification.
 */
export type BiomarkerGroup = 'lipids' | 'glucose' | 'bp' | 'body';

export const GROUP_OF: Record<string, BiomarkerGroup> = {
  LDL: 'lipids', HDL: 'lipids', TG: 'lipids', TC: 'lipids',
  HbA1c: 'glucose', FPG: 'glucose',
  SBP: 'bp', DBP: 'bp',
  BMI: 'body',
};

export const GROUP_LABEL: Record<BiomarkerGroup, string> = {
  lipids: 'Lipids',
  glucose: 'Glucose',
  bp: 'Blood pressure',
  body: 'Body',
};

export const GROUP_ORDER: BiomarkerGroup[] = ['lipids', 'glucose', 'bp', 'body'];

export function groupClass(biomarker: string): string {
  const g = GROUP_OF[biomarker] ?? 'body';
  return `grp-${g}`;
}

/** Full biomarker display names for tooltips/labels. */
export const BIOMARKER_NAME: Record<string, string> = {
  LDL: 'LDL cholesterol', HDL: 'HDL cholesterol', TG: 'Triglycerides', TC: 'Total cholesterol',
  HbA1c: 'HbA1c', FPG: 'Fasting glucose', SBP: 'Systolic BP', DBP: 'Diastolic BP', BMI: 'BMI',
};
