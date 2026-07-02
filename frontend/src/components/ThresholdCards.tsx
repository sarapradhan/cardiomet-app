'use client';
/**
 * frontend/src/components/ThresholdCards.tsx  (Daylight)
 * Per-biomarker cards grouped by panel. Each card: name (+ SA tag when South
 * Asian context applies), status chip, large Space Mono value, a BenchmarkBar
 * vs the NHANES Non-Hispanic Asian median, the guideline range description, the
 * source guideline, and any SA note. Presentation only — values, categories,
 * benchmarks, and notes all come from the API.
 */
import type { ThresholdResult, BenchmarkPoint } from '@/lib/types';
import { chipClass, categoryTone } from '@/lib/categoryStyles';
import { BenchmarkBar } from '@/components/BenchmarkBar';
import { GROUP_OF, GROUP_LABEL, GROUP_ORDER, BIOMARKER_NAME, type BiomarkerGroup } from '@/lib/biomarkerMeta';

interface Props {
  results: ThresholdResult[];
  benchmarkData?: BenchmarkPoint[];
  missingBiomarkers?: string[];
}

// Biomarkers whose interpretation carries South Asian–specific context.
const SA_RELEVANT = new Set(['HDL', 'FPG', 'HbA1c', 'SBP', 'DBP', 'BMI']);

export function ThresholdCards({ results, benchmarkData = [] }: Props) {
  const benchOf = (bm: string) => benchmarkData.find((b) => b.biomarker === bm);

  const byGroup: Record<BiomarkerGroup, ThresholdResult[]> = { lipids: [], glucose: [], bp: [], body: [] };
  for (const r of results) (byGroup[GROUP_OF[r.biomarker] ?? 'body']).push(r);

  return (
    <section className="card" data-tour="values">
      <p className="eyebrow" style={{ marginBottom: 4 }}>Your values</p>
      <h2 className="display" style={{ fontSize: 22, marginBottom: 18 }}>Each number, on its guideline range</h2>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 22 }}>
        {GROUP_ORDER.filter((g) => byGroup[g].length).map((g) => (
          <div key={g}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
              <span style={{ width: 9, height: 9, borderRadius: 3, background: `var(--grp-${g})` }} />
              <span className="caption" style={{ fontWeight: 600, color: 'var(--ink-soft)' }}>{GROUP_LABEL[g]}</span>
              <span className="caption" style={{ marginLeft: 'auto', color: 'var(--ink-faint)' }}>{byGroup[g].length}</span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 12 }}>
              {byGroup[g].map((r) => {
                const missing = r.category === null;
                const b = benchOf(r.biomarker);
                const tone = categoryTone(r.category);
                const isSA = SA_RELEVANT.has(r.biomarker);
                // display scale for the bar: pad around p10..p90 when we have benchmark data
                let lo = 0, hi = 1;
                if (b) {
                  const span = (b.cohort_p90 - b.cohort_p10) || 1;
                  lo = b.cohort_p10 - span * 0.25;
                  hi = b.cohort_p90 + span * 0.25;
                  if (r.value !== null) { lo = Math.min(lo, r.value - span * 0.1); hi = Math.max(hi, r.value + span * 0.1); }
                }
                return (
                  <div key={r.biomarker} style={{
                    padding: 16, borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--hairline)', background: 'var(--surface)',
                    opacity: missing ? 0.7 : 1,
                  }}>
                    {/* header: name + SA tag + status chip */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 8 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--ink)' }}>
                          {BIOMARKER_NAME[r.biomarker] ?? r.biomarker}
                        </span>
                        {isSA && (
                          <span style={{
                            fontSize: 9, fontWeight: 700, letterSpacing: '.04em',
                            color: 'var(--primary)', background: 'var(--primary-tint)',
                            padding: '2px 5px', borderRadius: 5,
                          }}>SA</span>
                        )}
                      </div>
                      <span className={chipClass(r.category)}>
                        <span className="chip-dot" />{missing ? 'Not provided' : r.category}
                      </span>
                    </div>

                    {/* big value */}
                    <div style={{ marginTop: 10, display: 'flex', alignItems: 'baseline', gap: 5 }}>
                      <span className="num" style={{ fontSize: 30, fontWeight: 700, color: 'var(--ink)' }}>
                        {missing ? '—' : r.value}
                      </span>
                      <span className="caption">{r.unit}</span>
                    </div>

                    {/* benchmark bar */}
                    {!missing && b && (
                      <BenchmarkBar value={r.value} benchmark={b.cohort_median} low={lo} high={hi}
                        tone={tone} group={`grp-${g}`} unit={r.unit} />
                    )}

                    {/* range description + source */}
                    {!missing && (
                      <p className="caption" style={{ marginTop: 10, lineHeight: 1.5 }}>{r.category_description}</p>
                    )}
                    <p className="caption" style={{ marginTop: 6, color: 'var(--ink-faint)', fontSize: 10.5 }}>
                      {r.guideline_source}
                    </p>
                    {r.note && (
                      <p className="caption" style={{ marginTop: 6, color: 'var(--primary)', fontStyle: 'italic' }}>{r.note}</p>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
