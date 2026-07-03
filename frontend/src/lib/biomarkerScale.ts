/**
 * frontend/src/lib/biomarkerScale.ts
 * Visual range scales for the per-biomarker range bar on the results screen.
 *
 * Presentation only. The clinical status (the chip) is computed server-side in
 * sahc_risklens/clinical/thresholds.py and is the single source of truth; the
 * zones here are illustrative guideline bands so a reader can SEE where a value
 * falls relative to the standard cut-points. Zones run left -> right; `to` is the
 * upper bound of each band and the final zone ends at `max`.
 */
import type { ChipTone } from './categoryStyles';

export interface ScaleZone {
  to: number;
  tone: ChipTone;
}

export interface BiomarkerScale {
  min: number;
  max: number;
  zones: ScaleZone[];
}

export const BIOMARKER_SCALE: Record<string, BiomarkerScale> = {
  LDL:   { min: 50,  max: 200, zones: [{ to: 100,  tone: 'normal' }, { to: 160,  tone: 'elevated' }, { to: 200, tone: 'high' }] },
  HDL:   { min: 20,  max: 90,  zones: [{ to: 40,   tone: 'high' },   { to: 50,   tone: 'elevated' }, { to: 90,  tone: 'normal' }] },
  TG:    { min: 50,  max: 300, zones: [{ to: 150,  tone: 'normal' }, { to: 200,  tone: 'elevated' }, { to: 300, tone: 'high' }] },
  TC:    { min: 120, max: 300, zones: [{ to: 200,  tone: 'normal' }, { to: 240,  tone: 'elevated' }, { to: 300, tone: 'high' }] },
  FPG:   { min: 70,  max: 140, zones: [{ to: 100,  tone: 'normal' }, { to: 126,  tone: 'elevated' }, { to: 140, tone: 'high' }] },
  HbA1c: { min: 4.5, max: 9,   zones: [{ to: 5.7,  tone: 'normal' }, { to: 6.5,  tone: 'elevated' }, { to: 9,   tone: 'high' }] },
  SBP:   { min: 90,  max: 180, zones: [{ to: 120,  tone: 'normal' }, { to: 130,  tone: 'elevated' }, { to: 180, tone: 'high' }] },
  DBP:   { min: 60,  max: 120, zones: [{ to: 80,   tone: 'normal' }, { to: 90,   tone: 'elevated' }, { to: 120, tone: 'high' }] },
  BMI:   { min: 16,  max: 35,  zones: [{ to: 23,   tone: 'normal' }, { to: 27.5, tone: 'elevated' }, { to: 35,  tone: 'high' }] },
};

/**
 * Biomarkers carrying documented South Asian–specific interpretation cut-points
 * (lower BMI thresholds, lower protective-HDL floor, faster dysglycemia
 * progression, earlier-onset hypertension). Surfaced as a small "SA" tag.
 */
export const SA_FLAGGED: Set<string> = new Set(['BMI', 'HDL', 'FPG', 'HbA1c', 'SBP']);

/** Maps a chip tone to its CSS custom property (defined in globals.css). */
export const TONE_COLOR: Record<ChipTone, string> = {
  normal: 'var(--in-range)',
  elevated: 'var(--elevated)',
  high: 'var(--high)',
  missing: 'var(--missing)',
};
