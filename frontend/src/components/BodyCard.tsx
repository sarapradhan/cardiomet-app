'use client';
/**
 * frontend/src/components/BodyCard.tsx
 * "Your body" summary card: the BMI result on its own, paired alongside
 * RiskSnapshot at the top of the results screen (BMI is the only body-panel
 * biomarker, so it reads better as its own focused card than a lone group
 * lower in the Values section).
 */
import type { ThresholdResult, BenchmarkPoint } from '@/lib/types';
import { categoryTone, chipClass } from '@/lib/categoryStyles';
import { BIOMARKER_NAME } from '@/lib/biomarkerMeta';
import { SA_FLAGGED, TONE_COLOR } from '@/lib/biomarkerScale';
import { MetricRangeBar } from './MetricRangeBar';

interface Props {
  results: ThresholdResult[];
  benchmarkData?: BenchmarkPoint[];
}

export function BodyCard({ results, benchmarkData = [] }: Props) {
  const bmi = results.find((r) => r.biomarker === 'BMI');
  if (!bmi) return null;

  const missing = bmi.category === null || bmi.value === null;
  const tone = categoryTone(bmi.category);
  const bench = benchmarkData.find((b) => b.biomarker === 'BMI')?.cohort_median;

  return (
    <section className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 8 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: 12 }}>
        <p className="eyebrow" style={{ marginBottom: 0 }}>Your body</p>
        <span className="caption">Body · WHO Asian</span>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 7, minWidth: 0 }}>
          <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--ink)', whiteSpace: 'nowrap' }}>
            {BIOMARKER_NAME.BMI ?? 'BMI'}
          </span>
          {SA_FLAGGED.has('BMI') && (
            <span title="South Asian–specific interpretation applies" style={{
              fontSize: 9, fontWeight: 700, letterSpacing: '0.04em', color: 'var(--primary)',
              background: 'var(--primary-tint)', padding: '2px 5px', borderRadius: 5, flex: 'none',
            }}>SA</span>
          )}
        </div>
        <span className={chipClass(bmi.category)}>
          <span className="chip-dot" />{missing ? 'Not provided' : bmi.category}
        </span>
      </div>

      <div style={{ display: 'flex', alignItems: 'baseline', gap: 5 }}>
        <span className="num" style={{ fontSize: 28, fontWeight: 600, lineHeight: 1, color: 'var(--ink)' }}>
          {missing ? '—' : bmi.value}
        </span>
        <span className="caption">{bmi.unit}</span>
      </div>

      {!missing && (
        <MetricRangeBar biomarker="BMI" value={bmi.value as number} tone={tone} benchmark={bench} />
      )}

      {!missing && (
        <div className="num" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: 10.5, color: 'var(--ink-faint)' }}>
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5 }}>
            <span style={{ width: 7, height: 7, borderRadius: 2, background: TONE_COLOR[tone], flex: 'none' }} />You {bmi.value}
          </span>
          {bench !== undefined && (
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5 }}>
              <span style={{ width: 8, height: 8, borderRadius: 999, border: '1.5px solid var(--ink-faint)', boxSizing: 'border-box', flex: 'none' }} />Benchmark {bench}
            </span>
          )}
        </div>
      )}

      {!missing && bmi.category_description && (
        <p className="caption" style={{ lineHeight: 1.5 }}>{bmi.category_description}</p>
      )}
      {bmi.note && <p className="caption" style={{ color: 'var(--primary)', fontStyle: 'italic' }}>{bmi.note}</p>}
    </section>
  );
}
