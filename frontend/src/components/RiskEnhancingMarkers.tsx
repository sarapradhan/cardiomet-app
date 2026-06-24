'use client';
/**
 * frontend/src/components/RiskEnhancingMarkers.tsx
 * Advanced lipid risk-enhancing markers (ApoB, Lp(a)). These are
 * classification-only — there is no population benchmark for them — so they are
 * shown separately from the benchmarked panel, framed as guideline-recognized
 * risk-enhancing factors. Renders nothing when the patient supplied neither.
 */
import type { ThresholdResult } from '@/lib/types';
import { chipClass } from '@/lib/categoryStyles';
import { BIOMARKER_NAME } from '@/lib/biomarkerMeta';

export function RiskEnhancingMarkers({ markers }: { markers: ThresholdResult[] }) {
  if (!markers || markers.length === 0) return null;

  return (
    <section className="card">
      <p className="eyebrow" style={{ marginBottom: 4 }}>Risk-enhancing markers</p>
      <h2 className="title" style={{ marginBottom: 6 }}>Advanced lipid markers</h2>
      <p className="caption" style={{ marginBottom: 18, lineHeight: 1.5, color: 'var(--ink-soft)' }}>
        ApoB and Lp(a) are recognized as risk-enhancing factors in the 2018 AHA/ACC
        Cholesterol Guideline and are particularly relevant to South Asian risk.
        They are shown here as guideline context for discussion with your clinician —
        classified against guideline cut-points, not compared against a population
        benchmark, and not an individual risk score.
      </p>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(208px, 1fr))', gap: 10 }}>
        {markers.map((r) => (
          <div key={r.biomarker} style={{
            display: 'flex', gap: 12, padding: 14, borderRadius: 'var(--radius-sm)',
            border: '1px solid var(--hairline)', background: 'var(--surface)',
          }}>
            <span className="grp-tag grp-lipids" />
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: 8 }}>
                <span style={{ fontSize: 12.5, fontWeight: 600, color: 'var(--ink)' }}>{r.biomarker}</span>
                <span className="num" style={{ fontSize: 17, fontWeight: 600, color: 'var(--ink)' }}>
                  {r.value}
                  <span className="caption" style={{ marginLeft: 3, fontWeight: 400 }}>{r.unit}</span>
                </span>
              </div>
              <div style={{ marginTop: 8 }}>
                <span className={chipClass(r.category)}><span className="chip-dot" />{r.category}</span>
              </div>
              <p className="caption" style={{ marginTop: 8, lineHeight: 1.5 }}>{r.category_description}</p>
              <p className="caption" style={{ marginTop: 6, color: 'var(--ink-faint)', fontSize: 10.5 }}>
                {BIOMARKER_NAME[r.biomarker] ?? r.biomarker} · {r.guideline_source}
              </p>
              {r.note && <p className="caption" style={{ marginTop: 4, color: 'var(--primary)', fontStyle: 'italic' }}>{r.note}</p>}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
