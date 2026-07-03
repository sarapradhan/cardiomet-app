'use client';
/**
 * frontend/src/components/InputRecap.tsx
 * "Your inputs" recap chips with an Adjust link back to the form. Demographics come
 * from the stored BiomarkerInput when available; the per-biomarker values are read
 * back from the threshold results so the recap matches exactly what was scored.
 */
import Link from 'next/link';
import type { BiomarkerInput, ThresholdResult } from '@/lib/types';

interface Chip {
  label: string;
  value: string;
}

interface Props {
  results: ThresholdResult[];
  input?: BiomarkerInput | null;
}

export function InputRecap({ results, input }: Props) {
  const chips: Chip[] = [];

  if (input) {
    if (input.age_yr != null) chips.push({ label: 'Age', value: String(input.age_yr) });
    if (input.sex) chips.push({ label: 'Sex', value: input.sex === 'M' ? 'Male' : 'Female' });
    if (input.south_asian) chips.push({ label: 'Ancestry', value: 'South Asian' });
  }

  for (const r of results) {
    if (r.value != null) chips.push({ label: r.biomarker, value: `${r.value} ${r.unit}` });
  }

  if (chips.length === 0) return null;

  return (
    <section className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12, marginBottom: 14 }}>
        <p className="eyebrow" style={{ marginBottom: 0 }}>Your inputs</p>
        <Link href="/benchmark" className="btn btn-outline" style={{ height: 32, fontSize: 12.5, padding: '0 14px' }}>
          Adjust
        </Link>
      </div>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
        {chips.map((c, i) => (
          <span key={i} style={{
            display: 'inline-flex', alignItems: 'center', gap: 6, padding: '6px 11px',
            borderRadius: 'var(--radius-sm)', background: 'var(--surface-sunken)', fontSize: 12,
          }}>
            <span style={{ color: 'var(--ink-faint)' }}>{c.label}</span>
            <span className="num" style={{ color: 'var(--ink)', fontWeight: 600 }}>{c.value}</span>
          </span>
        ))}
      </div>
    </section>
  );
}
