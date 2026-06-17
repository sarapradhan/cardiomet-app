'use client';
/**
 * frontend/src/components/ThresholdCards.tsx
 * One card per biomarker showing the patient's value, its clinical category as a
 * Material Design chip, the range, and the guideline source. Missing biomarkers
 * render a muted "missing" chip rather than being omitted, so the person can see
 * what wasn't provided.
 */
import type { ThresholdResult } from '@/lib/types';
import { chipClass } from '@/lib/categoryStyles';

interface Props {
  results: ThresholdResult[];
  missingBiomarkers: string[];
}

export function ThresholdCards({ results }: Props) {
  return (
    <section className="md-card" style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
      <p className="md-label" style={{ marginBottom: 4 }}>Clinical Thresholds</p>
      <h2 className="md-title" style={{ marginBottom: 16 }}>Your Values in Context</h2>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 12 }}>
        {results.map((r) => {
          const missing = r.category === null;
          return (
            <div key={r.biomarker} className="md-surface-variant"
              style={{ display: 'flex', flexDirection: 'column', gap: 8, opacity: missing ? 0.7 : 1 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
                <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--md-on-surface)' }}>
                  {r.biomarker}
                </span>
                <span style={{ fontSize: 18, fontWeight: 300, color: 'var(--md-on-surface)' }}>
                  {missing ? '—' : r.value}
                  <span style={{ fontSize: 11, color: 'var(--md-on-surface-variant)', marginLeft: 4 }}>
                    {r.unit}
                  </span>
                </span>
              </div>
              <span className={chipClass(r.category)}>
                {missing ? 'Not provided' : r.category}
              </span>
              {!missing && (
                <span style={{ fontSize: 11, color: 'var(--md-on-surface-variant)' }}>
                  {r.category_description}
                </span>
              )}
              <span style={{ fontSize: 10, color: 'var(--md-outline)' }}>
                {r.guideline_source}
              </span>
              {r.note && (
                <span style={{ fontSize: 10, color: 'var(--md-secondary)', fontStyle: 'italic' }}>
                  {r.note}
                </span>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
}
