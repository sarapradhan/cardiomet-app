'use client';
/**
 * frontend/src/components/DistributionChart.tsx
 * Percentile band (p10–p90, p25–p75 emphasized) per biomarker with the patient's
 * marker. Markers use the biomarker group hue. Reference is labeled exactly
 * (NHANES Non-Hispanic Asian) — never described as South Asian-specific.
 */
import type { BenchmarkPoint } from '@/lib/types';
import { GROUP_OF } from '@/lib/biomarkerMeta';

function norm(v: number, lo: number, hi: number): number {
  if (hi === lo) return 50;
  return Math.max(0, Math.min(100, ((v - lo) / (hi - lo)) * 100));
}

export function DistributionChart({ benchmarkData, cohortLabel }: { benchmarkData: BenchmarkPoint[]; cohortLabel: string }) {
  return (
    <section className="card">
      <p className="eyebrow" style={{ marginBottom: 4 }}>Population benchmark</p>
      <h2 className="title" style={{ marginBottom: 6 }}>Where you sit in the distribution</h2>
      <p className="body" style={{ marginBottom: 20 }}>
        Reference: {cohortLabel}. The bar spans the 10th–90th percentile; the solid
        segment is the 25th–75th. Your value is the dot.
      </p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        {benchmarkData.map((b) => {
          const span = b.cohort_p90 - b.cohort_p10 || 1;
          const lo = b.cohort_p10 - span * 0.18, hi = b.cohort_p90 + span * 0.18;
          const p10 = norm(b.cohort_p10, lo, hi), p25 = norm(b.cohort_p25, lo, hi);
          const p75 = norm(b.cohort_p75, lo, hi), p90 = norm(b.cohort_p90, lo, hi);
          const med = norm(b.cohort_median, lo, hi);
          const has = b.patient_value !== null && b.patient_value !== undefined;
          const px = has ? norm(b.patient_value as number, lo, hi) : 0;
          const g = GROUP_OF[b.biomarker] ?? 'body';

          return (
            <div key={b.biomarker}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6, alignItems: 'baseline' }}>
                <span style={{ fontSize: 12.5, fontWeight: 600, color: 'var(--ink)' }}>{b.biomarker}</span>
                <span className="caption num">
                  {has ? <>you <strong style={{ color: 'var(--ink)' }}>{b.patient_value}</strong> · </> : 'not provided · '}
                  median {b.cohort_median} · n={b.cohort_n}
                </span>
              </div>
              <div style={{ position: 'relative', height: 22 }}>
                <div style={{ position: 'absolute', top: 9, left: 0, right: 0, height: 4, borderRadius: 2, background: 'var(--surface-sunken)' }} />
                <div style={{ position: 'absolute', top: 9, height: 4, borderRadius: 2, left: `${p10}%`, width: `${p90 - p10}%`, background: 'var(--hairline)' }} />
                <div style={{ position: 'absolute', top: 7, height: 8, borderRadius: 4, left: `${p25}%`, width: `${p75 - p25}%`, background: `var(--grp-${g})`, opacity: 0.32 }} />
                <div style={{ position: 'absolute', top: 4, height: 14, width: 1.5, left: `${med}%`, background: 'var(--ink-faint)' }} />
                {has && (
                  <div title={`You: ${b.patient_value}`} style={{
                    position: 'absolute', top: 4, height: 14, width: 14, borderRadius: '50%',
                    left: `calc(${px}% - 7px)`, background: `var(--grp-${g})`,
                    border: '2.5px solid #fff', boxShadow: 'var(--shadow-1)',
                  }} />
                )}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
