'use client';
/**
 * frontend/src/components/RiskSnapshot.tsx
 * Top-of-results summary: how many reported markers land in range / elevated / high,
 * shown as a stacked bar plus a one-line headline. Counts use the same tone mapping
 * (categoryStyles) as the chips, so the snapshot can never disagree with the cards.
 */
import type { ThresholdResult } from '@/lib/types';
import { categoryTone } from '@/lib/categoryStyles';

export function RiskSnapshot({ results }: { results: ThresholdResult[] }) {
  let normal = 0, elevated = 0, high = 0, missing = 0;
  for (const r of results) {
    const t = categoryTone(r.category);
    if (t === 'normal') normal++;
    else if (t === 'elevated') elevated++;
    else if (t === 'high') high++;
    else missing++;
  }

  const reported = normal + elevated + high;
  const watch = elevated + high;
  const total = results.length;
  const seg = (n: number) => (reported ? (n / reported) * 100 : 0);

  const headline = reported === 0
    ? 'No markers reported yet'
    : watch === 0
      ? 'All reported markers in range'
      : `${watch} marker${watch === 1 ? '' : 's'} to review`;

  const legend: [string, number, string][] = [
    ['In range', normal, 'var(--in-range)'],
    ['Elevated', elevated, 'var(--elevated)'],
    ['High', high, 'var(--high)'],
  ];

  return (
    <section className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', gap: 8 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: 12 }}>
        <p className="eyebrow" style={{ marginBottom: 0 }}>Your snapshot</p>
        <span className="caption num">{reported} of {total} reported</span>
      </div>

      <h2 className="display" style={{ fontSize: 24, marginTop: 8 }}>{headline}</h2>
      <p className="body" style={{ marginTop: 2 }}>
        {normal} in range · {elevated} elevated · {high} high{missing ? ` · ${missing} not provided` : ''}
      </p>

      <div style={{
        display: 'flex', height: 10, borderRadius: 999, overflow: 'hidden',
        marginTop: 16, background: 'var(--surface-sunken)',
      }}>
        {normal > 0 && <div style={{ width: `${seg(normal)}%`, background: 'var(--in-range)' }} />}
        {elevated > 0 && <div style={{ width: `${seg(elevated)}%`, background: 'var(--elevated)' }} />}
        {high > 0 && <div style={{ width: `${seg(high)}%`, background: 'var(--high)' }} />}
      </div>

      <div style={{ display: 'flex', gap: 18, marginTop: 12, flexWrap: 'wrap' }}>
        {legend.map(([label, n, c]) => (
          <span key={label} style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 12, color: 'var(--ink-soft)' }}>
            <span style={{ width: 8, height: 8, borderRadius: 3, background: c, flex: 'none' }} />
            <span className="num" style={{ fontWeight: 600, color: 'var(--ink)' }}>{n}</span> {label}
          </span>
        ))}
      </div>
    </section>
  );
}
