/**
 * frontend/src/lib/healthFile.ts
 * User-owned, portable "health file" handling. This is how longitudinal tracking
 * works with NO server storage — the patient owns the JSON file and (optionally)
 * a local browser cache they control. Mirrors the server health-file schema.
 */
import type { BiomarkerSeries } from './types';

const SCHEMA_VERSION = '1.0';
const LOCAL_KEY = 'sahc_health_file_v1';

interface HealthFileDoc {
  schema_version: string;
  exported_at: string;
  series: BiomarkerSeries;
}

export function buildHealthFile(series: BiomarkerSeries): HealthFileDoc {
  return {
    schema_version: SCHEMA_VERSION,
    exported_at: new Date().toISOString(),
    series,
  };
}

/** Trigger a browser download of the series as a portable JSON file. */
export function exportHealthFile(series: BiomarkerSeries): void {
  const doc = buildHealthFile(series);
  const blob = new Blob([JSON.stringify(doc, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `sahc-risklens-health-file-${new Date().toISOString().slice(0, 10)}.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

/** Parse + validate an imported health file's text into a series. Throws on bad schema. */
export function parseHealthFile(text: string): BiomarkerSeries {
  let doc: unknown;
  try {
    doc = JSON.parse(text);
  } catch {
    throw new Error('That file is not valid JSON.');
  }
  const d = doc as Partial<HealthFileDoc>;
  if (!d || d.schema_version !== SCHEMA_VERSION) {
    throw new Error('Unsupported or missing health-file version.');
  }
  if (!d.series || !Array.isArray(d.series.draws) || d.series.draws.length === 0) {
    throw new Error('Health file contains no draws.');
  }
  return d.series;
}

/** Optional local cache — on the user's own device, user-controlled. */
export function saveLocal(series: BiomarkerSeries): void {
  try { localStorage.setItem(LOCAL_KEY, JSON.stringify(buildHealthFile(series))); }
  catch { /* storage unavailable; non-fatal */ }
}

export function loadLocal(): BiomarkerSeries | null {
  try {
    const raw = localStorage.getItem(LOCAL_KEY);
    if (!raw) return null;
    return parseHealthFile(raw);
  } catch {
    return null;
  }
}

export function clearLocal(): void {
  try { localStorage.removeItem(LOCAL_KEY); } catch { /* non-fatal */ }
}
