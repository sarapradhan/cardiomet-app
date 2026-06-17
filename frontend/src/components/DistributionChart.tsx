'use client';
/**
 * frontend/src/components/DistributionChart.tsx
 * For each biomarker, shows the NHANES Non-Hispanic Asian cohort percentile band
 * (p10–p90, with p25–p75 emphasized) and overlays the patient's own value as a
 * marker. Uses a normalized 0–100 horizontal scale per biomarker so disparate
 * units share one row layout.
 *
 * The cohort_label is shown verbatim from the API. This is a benchmark against
 * the NHANES Non-Hispanic Asian sample — never described as a South Asian cohort.
 */
import type { BenchmarkPoint } from '@/lib/types';

interface Props {
  benchmarkData: BenchmarkPoint[];
  cohortLabel: string;
}

function normalize(value: number, lo: number, hi: number): number {
  if (hi === lo) return 50;
  return Math.max(0, Math.min(100, ((value - lo) / (hi - lo)) * 100));
}

export function DistributionChart({ benchmarkData, cohortLabel }: Props) {
  return (
    <section className="md-card" style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
      <p className="md-label" style={{ marginBottom: 4 }}>Population Benchmark</p>
      <h2 className="md-title" style={{ marginBottom: 4 }}>Where You Sit in the Distribution</h2>
      <p className="md-body" style={{ marginBottom: 20 }}>
        Reference cohort: {cohortLabel}. Bars span the 10th–90th percentile; the
        darker segment is the 25th–75th. Your value is marked with a dot.
      </p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
        {benchmarkData.map((b) => {
          // Axis padding so p10/p90 don't sit on the extreme edges.
          const span = b.cohort_p90 - b.cohort_p10 || 1;
          const axisLo = b.cohort_p10 - span * 0.15;
          const axisHi = b.cohort_p90 + span * 0.15;

          const p10 = normalize(b.cohort_p10, axisLo, axisHi);
          const p25 = normalize(b.cohort_p25, axisLo, axisHi);
          const p75 = normalize(b.cohort_p75, axisLo, axisHi);
          const p90 = normalize(b.cohort_p90, axisLo, axisHi);
          const med = normalize(b.cohort_median, axisLo, axisHi);
          const hasPatient = b.patient_value !== null && b.patient_value !== undefined;
          const patient = hasPatient ? normalize(b.patient_value as number, axisLo, axisHi) : 0;

          return (
            <div key={b.biomarker}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                <span style={{ fontSize: 13, fontWeight: 600 }}>{b.biomarker}</span>
                <span style={{ fontSize: 11, color: 'var(--md-on-surface-variant)' }}>
                  {hasPatient ? `You: ${b.patient_value}` : 'Not provided'}
                  {'  ·  '}median {b.cohort_median} · n={b.cohort_n}
                </span>
              </div>

              {/* Track */}
              <div style={{ position: 'relative', height: 24, borderRadius: 12,
                background: 'var(--md-surface-variant)' }}>
                {/* p10–p90 band */}
                <div style={{ position: 'absolute', top: 8, height: 8, borderRadius: 4,
                  left: `${p10}%`, width: `${p90 - p10}%`, background: 'var(--md-outline-variant)' }} />
                {/* p25–p75 band */}
                <div style={{ position: 'absolute', top: 6, height: 12, borderRadius: 6,
                  left: `${p25}%`, width: `${p75 - p25}%`, background: 'var(--md-primary-container)' }} />
                {/* median tick */}
                <div style={{ position: 'absolute', top: 3, height: 18, width: 2,
                  left: `calc(${med}% - 1px)`, background: 'var(--md-secondary)' }} />
                {/* patient marker */}
                {hasPatient && (
                  <div title={`You: ${b.patient_value}`} style={{
                    position: 'absolute', top: 4, height: 16, width: 16, borderRadius: '50%',
                    left: `calc(${patient}% - 8px)`, background: 'var(--md-primary)',
                    border: '2px solid #fff', boxShadow: 'var(--md-elevation-1)' }} />
                )}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
