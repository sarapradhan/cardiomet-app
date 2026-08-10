'use client';
/**
 * frontend/src/components/ThresholdCards.tsx
 * Per-biomarker cards grouped by panel. Each card places the value on its guideline
 * range (MetricRangeBar) with the population median as a benchmark ring, alongside a
 * clinical-status chip and — where relevant — a South Asian context tag. The chip and
 * legend colours are the legend in action; the range zones add visual context.
 *
 * The Body panel (BMI) is rendered separately by <BodyCard> above this section, so
 * it's intentionally excluded here. Glucose and Blood pressure share one section
 * (each keeping its own group-color label) so their four cards read as one row.
 */
import type { ThresholdResult, BenchmarkPoint } from '@/lib/types';
import { categoryTone, chipClass } from '@/lib/categoryStyles';
import { GROUP_OF, GROUP_LABEL, BIOMARKER_NAME, type BiomarkerGroup } from '@/lib/biomarkerMeta';
import { SA_FLAGGED, TONE_COLOR } from '@/lib/biomarkerScale';
import { MetricRangeBar } from './MetricRangeBar';

interface Props {
  results: ThresholdResult[];
  benchmarkData?: BenchmarkPoint[];
  missingBiomarkers?: string[];
}

const SECTIONS: { key: string; groups: BiomarkerGroup[] }[] = [
  { key: 'lipids', groups: ['lipids'] },
  { key: 'glucose-bp', groups: ['glucose', 'bp'] },
];

export function ThresholdCards({ results, benchmarkData = [] }: Props) {
  const benchOf: Record<string, number> = {};
  for (const b of benchmarkData) benchOf[b.biomarker] = b.cohort_median;

  const byGroup: Record<BiomarkerGroup, ThresholdResult[]> = { lipids: [], glucose: [], bp: [], body: [] };
  for (const r of results) (byGroup[GROUP_OF[r.biomarker] ?? 'body']).push(r);

  const sections = SECTIONS
    .map((s) => ({ ...s, items: s.groups.flatMap((g) => byGroup[g]) }))
    .filter((s) => s.items.length);

  return (
    <section className="card">
      <p className="eyebrow" style={{ marginBottom: 4 }}>Your values</p>
      <h2 className="title" style={{ marginBottom: 18 }}>Each number, on its guideline range</h2>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 22 }}>
        {sections.map(({ key, groups, items }) => (
          <div key={key}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 12, flexWrap: 'wrap' }}>
              {groups.filter((g) => byGroup[g].length).map((g) => (
                <span key={g} style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ width: 10, height: 10, borderRadius: 3, background: `var(--grp-${g})`, flex: 'none' }} />
                  <span className="caption" style={{ fontWeight: 600, color: 'var(--ink-soft)' }}>{GROUP_LABEL[g]}</span>
                </span>
              ))}
              <span style={{ flex: 1, height: 1, background: 'var(--hairline)', minWidth: 20 }} />
              <span className="caption" style={{ color: 'var(--ink-faint)' }}>{items.length}</span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 10 }}>
              {items.map((r) => {
                // Two distinct null-category states: a value that was never
                // entered (missing) vs. a value that WAS entered but can't be
                // classified — e.g. FPG without confirmed fasting status. The
                // latter must still show the patient's value and the reason,
                // not collapse to the same "Not provided" treatment.
                const missing = r.value === null;
                const unclassified = !missing && r.category === null;
                const tone = categoryTone(r.category);
                const bench = benchOf[r.biomarker];
                return (
                  <div key={r.biomarker} style={{
                    padding: 16, borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--hairline)', background: 'var(--surface)',
                    boxShadow: 'var(--shadow-1)', opacity: missing ? 0.7 : 1,
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 7, minWidth: 0 }}>
                        <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--ink)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                          {BIOMARKER_NAME[r.biomarker] ?? r.biomarker}
                        </span>
                        {SA_FLAGGED.has(r.biomarker) && (
                          <span title="South Asian–specific interpretation applies" style={{
                            fontSize: 9, fontWeight: 700, letterSpacing: '0.04em', color: 'var(--primary)',
                            background: 'var(--primary-tint)', padding: '2px 5px', borderRadius: 5, flex: 'none',
                          }}>SA</span>
                        )}
                      </div>
                      <span className={chipClass(r.category)}>
                        <span className="chip-dot" />
                        {missing ? 'Not provided' : unclassified ? 'Not classified' : r.category}
                      </span>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'baseline', gap: 5, marginTop: 10 }}>
                      <span className="num" style={{ fontSize: 28, fontWeight: 600, lineHeight: 1, color: 'var(--ink)' }}>
                        {missing ? '—' : r.value}
                      </span>
                      <span className="caption">{r.unit}</span>
                    </div>

                    {/* Range bar needs a category to place the tone/zone — skip
                        for unclassified values (e.g. FPG pending fasting
                        confirmation) rather than imply a category that wasn't
                        actually assigned. */}
                    {!missing && !unclassified && (
                      <MetricRangeBar biomarker={r.biomarker} value={r.value as number} tone={tone} benchmark={bench} />
                    )}

                    {!missing && !unclassified && (
                      <div className="num" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: 10.5, color: 'var(--ink-faint)' }}>
                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5 }}>
                          <span style={{ width: 7, height: 7, borderRadius: 2, background: TONE_COLOR[tone], flex: 'none' }} />You {r.value}
                        </span>
                        {bench !== undefined && (
                          <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5 }}>
                            <span style={{ width: 8, height: 8, borderRadius: 999, border: '1.5px solid var(--ink-faint)', boxSizing: 'border-box', flex: 'none' }} />Benchmark {bench}
                          </span>
                        )}
                      </div>
                    )}

                    {!missing && r.category_description && (
                      <p className="caption" style={{ marginTop: 10, lineHeight: 1.5 }}>{r.category_description}</p>
                    )}
                    <p className="caption" style={{ marginTop: 6, color: 'var(--ink-faint)', fontSize: 10.5 }}>{r.guideline_source}</p>
                    {r.note && <p className="caption" style={{ marginTop: 4, color: 'var(--primary)', fontStyle: 'italic' }}>{r.note}</p>}
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
