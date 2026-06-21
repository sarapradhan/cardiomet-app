'use client';
/**
 * frontend/src/components/SouthAsianContextPanel.tsx
 * Renders the guideline-backed South Asian risk-enhancing context. This is
 * qualitative clinical context for physician discussion — it is explicitly not
 * a risk score and not the NHANES benchmark. Text comes verbatim from the API.
 */
import type { SouthAsianContextItem } from '@/lib/types';

interface Props {
  items: SouthAsianContextItem[];
}

export function SouthAsianContextPanel({ items }: Props) {
  if (items.length === 0) return null;
  return (
    <section className="card" style={{ display: 'flex', flexDirection: 'column', gap: 4,
      borderLeft: '4px solid var(--grp-bp)' }}>
      <p className="eyebrow" style={{ marginBottom: 4 }}>Risk Context</p>
      <h2 className="title" style={{ marginBottom: 16 }}>South Asian Considerations</h2>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        {items.map((item, i) => (
          <div key={i} style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            <span style={{ fontSize: 14, fontWeight: 600, color: 'var(--ink)' }}>
              {item.factor}
            </span>
            <span style={{ fontSize: 13, lineHeight: 1.6, color: 'var(--ink-soft)' }}>
              {item.description}
            </span>
            <span style={{ fontSize: 10, color: 'var(--ink-faint)' }}>
              {item.guideline_source}
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}
