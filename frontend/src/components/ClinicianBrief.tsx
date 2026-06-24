'use client';
/**
 * frontend/src/components/ClinicianBrief.tsx
 * A concise, clinician-oriented summary the patient can bring (or send) to their
 * appointment. Compiled entirely from the existing BenchmarkResponse — no new
 * API surface. Highlights out-of-range values, advanced markers, South Asian
 * context, medications, and missing data, and offers a copy-to-clipboard plain
 * text version for pasting into a note. Educational summary — not a diagnosis.
 */
import { useState } from 'react';
import type { BenchmarkResponse, ThresholdResult } from '@/lib/types';
import { BIOMARKER_NAME } from '@/lib/biomarkerMeta';

// Categories considered within range (everything else is flagged "notable").
const NORMAL = new Set([
  'Optimal', 'Near Optimal', 'Normal', 'Desirable', 'Protective', 'Within range',
]);

const isNotable = (r: ThresholdResult) => r.category !== null && !NORMAL.has(r.category);

function buildText(result: BenchmarkResponse): string {
  const lines: string[] = [];
  lines.push('PRE-VISIT SUMMARY (educational — not a diagnosis)');
  lines.push(`Reference cohort: ${result.cohort_label}` +
    (result.matched && result.match_description ? ` · matched peers: ${result.match_description}` : ''));
  lines.push('');

  const provided = result.threshold_results.filter((r) => r.category !== null);
  const notable = provided.filter(isNotable);
  if (notable.length) {
    lines.push('Out-of-range values:');
    for (const r of notable) {
      lines.push(`  • ${BIOMARKER_NAME[r.biomarker] ?? r.biomarker}: ${r.value} ${r.unit} — ` +
        `${r.category} (${r.guideline_source})`);
    }
  } else {
    lines.push('Out-of-range values: none among provided values.');
  }

  const inRange = provided.filter((r) => !isNotable(r));
  if (inRange.length) {
    lines.push('');
    lines.push('Within range: ' +
      inRange.map((r) => `${r.biomarker} ${r.value}${r.unit} (${r.category})`).join('; '));
  }

  if (result.risk_enhancing_markers.length) {
    lines.push('');
    lines.push('Advanced lipid markers (classification-only, not benchmarked):');
    for (const r of result.risk_enhancing_markers) {
      lines.push(`  • ${r.biomarker}: ${r.value} ${r.unit} — ${r.category} (${r.guideline_source})`);
    }
  }

  if (result.south_asian_context.length) {
    lines.push('');
    lines.push('South Asian context: ' +
      result.south_asian_context.map((i) => i.factor).join('; '));
  }

  if (result.medication_notes.length) {
    lines.push('');
    lines.push('Medication notes: ' + result.medication_notes.join(' '));
  }

  if (result.care_navigation.length) {
    lines.push('');
    lines.push('Discussion topics: ' +
      result.care_navigation.map((i) => i.title).join('; '));
  }

  if (result.missing_biomarkers.length) {
    lines.push('');
    lines.push(`Not provided: ${result.missing_biomarkers.join(', ')}`);
  }

  lines.push('');
  lines.push(result.disclaimer);
  return lines.join('\n');
}

export function ClinicianBrief({ result }: { result: BenchmarkResponse }) {
  const [copied, setCopied] = useState(false);
  const text = buildText(result);

  async function copy() {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      /* clipboard unavailable — the text is visible to select manually */
    }
  }

  return (
    <section className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: 12, flexWrap: 'wrap' }}>
        <div>
          <p className="eyebrow" style={{ marginBottom: 4 }}>For your clinician</p>
          <h2 className="title" style={{ marginBottom: 4 }}>Pre-visit summary</h2>
        </div>
        <button className="btn btn-outline" style={{ height: 34, fontSize: 13 }} onClick={copy}>
          {copied ? 'Copied ✓' : 'Copy summary'}
        </button>
      </div>
      <p className="caption" style={{ marginBottom: 14, color: 'var(--ink-soft)', lineHeight: 1.5 }}>
        A concise summary to bring to your appointment. Educational only — it does not
        diagnose or recommend treatment.
      </p>
      <pre style={{
        whiteSpace: 'pre-wrap', wordBreak: 'break-word', margin: 0, padding: 16,
        background: 'var(--panel-sunken)', borderRadius: 'var(--radius-sm)',
        fontFamily: 'var(--font-mono, ui-monospace, SFMono-Regular, Menlo, monospace)',
        fontSize: 12.5, lineHeight: 1.6, color: 'var(--ink)',
      }}>{text}</pre>
    </section>
  );
}
