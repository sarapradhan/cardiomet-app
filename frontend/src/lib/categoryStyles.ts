/**
 * frontend/src/lib/categoryStyles.ts
 * Maps a clinical category string to one of the Material Design chip classes
 * defined in globals.css (chip-normal / chip-elevated / chip-high / chip-missing).
 *
 * This is presentation only — it never changes the clinical category, which is
 * computed server-side in sahc_risklens/clinical/thresholds.py. The grouping
 * mirrors the appendix: lowest-risk categories read as "normal", intermediate as
 * "elevated", and the most severe as "high".
 */

const HIGH = new Set([
  'High',
  'Very High',
  'Diabetes',
  'Stage 2 Hypertension',
  'High risk',
  'Obese',
]);

const ELEVATED = new Set([
  'Near Optimal',
  'Borderline High',
  'Prediabetes',
  'Elevated',
  'Stage 1 Hypertension',
  'Increased risk',
  'Overweight',
  'Underweight',
  'Low', // low HDL is a cardiovascular risk signal
]);

const NORMAL = new Set([
  'Optimal',
  'Normal',
  'Desirable',
  'Protective',
]);

export type ChipTone = 'normal' | 'elevated' | 'high' | 'missing';

export function categoryTone(category: string | null): ChipTone {
  if (category === null) return 'missing';
  if (HIGH.has(category)) return 'high';
  if (ELEVATED.has(category)) return 'elevated';
  if (NORMAL.has(category)) return 'normal';
  return 'elevated'; // unknown but present — surface it rather than hide it
}

export function chipClass(category: string | null): string {
  return `chip chip-${categoryTone(category)}`;
}

// The status color for a category, as a CSS variable. Used to render category
// labels (Optimal, Protective, High, …) as colored text — consistent across the
// app and matching the distribution-bar accents.
const TONE_VAR: Record<ChipTone, string> = {
  normal: 'var(--in-range)',
  elevated: 'var(--elevated)',
  high: 'var(--high)',
  missing: 'var(--missing)',
};

export function toneColor(category: string | null): string {
  return TONE_VAR[categoryTone(category)];
}
