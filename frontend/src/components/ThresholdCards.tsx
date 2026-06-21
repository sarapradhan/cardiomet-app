'use client';
/**
 * frontend/src/components/ThresholdCards.tsx
 * Per-biomarker cards grouped by panel, each with its group color tag (left edge)
 * and a clinical-status chip. The group tag + status chip are the legend in action.
 */
import type { ThresholdResult } from '@/lib/types';
import { chipClass } from '@/lib/categoryStyles';
import { GROUP_OF, GROUP_LABEL, GROUP_ORDER, BIOMARKER_NAME, type BiomarkerGroup } from '@/lib/biomarkerMeta';

export function ThresholdCards({ results }: { results: ThresholdResult[]; missingBiomarkers?: string[] }) {
  const byGroup: Record<BiomarkerGroup, ThresholdResult[]> = { lipids: [], glucose: [], bp: [], body: [] };
  for (const r of results) (byGroup[GROUP_OF[r.biomarker] ?? 'body']).push(r);

  return (
    <section className="card">
      <p className="eyebrow" style={{ marginBottom: 4 }}>Your values</p>
      <h2 className="title" style={{ marginBottom: 18 }}>Each number, in clinical context</h2>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 22 }}>
        {GROUP_ORDER.filter((g) => byGroup[g].length).map((g) => (
          <div key={g}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
              <span style={{ width: 10, height: 10, borderRadius: 3, background: `var(--grp-${g})` }} />
              <span className="caption" style={{ fontWeight: 600, color: 'var(--ink-soft)' }}>{GROUP_LABEL[g]}</span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(208px, 1fr))', gap: 10 }}>
              {byGroup[g].map((r) => {
                const missing = r.category === null;
                return (
                  <div key={r.biomarker} style={{
                    display: 'flex', gap: 12, padding: 14, borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--hairline)', background: 'var(--surface)',
                    opacity: missing ? 0.72 : 1,
                  }}>
                    <span className={`grp-tag grp-${g}`} />
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: 8 }}>
                        <span style={{ fontSize: 12.5, fontWeight: 600, color: 'var(--ink)' }}>{r.biomarker}</span>
                        <span className="num" style={{ fontSize: 17, fontWeight: 600, color: 'var(--ink)' }}>
                          {missing ? '—' : r.value}
                          <span className="caption" style={{ marginLeft: 3, fontWeight: 400 }}>{r.unit}</span>
                        </span>
                      </div>
                      <div style={{ marginTop: 8 }}>
                        <span className={chipClass(r.category)}>
                          <span className="chip-dot" />{missing ? 'Not provided' : r.category}
                        </span>
                      </div>
                      {!missing && (
                        <p className="caption" style={{ marginTop: 8, lineHeight: 1.5 }}>{r.category_description}</p>
                      )}
                      <p className="caption" style={{ marginTop: 6, color: 'var(--ink-faint)', fontSize: 10.5 }}>
                        {BIOMARKER_NAME[r.biomarker] ?? r.biomarker} · {r.guideline_source}
                      </p>
                      {r.note && <p className="caption" style={{ marginTop: 4, color: 'var(--primary)', fontStyle: 'italic' }}>{r.note}</p>}
                    </div>
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
