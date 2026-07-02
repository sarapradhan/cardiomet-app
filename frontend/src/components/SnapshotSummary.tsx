'use client';
/**
 * frontend/src/components/SnapshotSummary.tsx
 * Daylight "Your snapshot" overview: how many markers were reported and how they
 * distribute across in-range / elevated / high, with a segmented bar. Counts are
 * derived from the API's threshold_results via the shared tone helper — no new
 * clinical logic. Descriptive only; no scores, no risk language.
 */
import type { ThresholdResult } from '@/lib/types';
import { categoryTone } from '@/lib/categoryStyles';

export function SnapshotSummary({ results }: { results: ThresholdResult[] }) {
  const reported = results.filter((r) => r.category !== null);
  const total = results.length;
  let inRange = 0, elevated = 0, high = 0;
  for (const r of reported) {
    const t = categoryTone(r.category);
    if (t === 'normal') inRange++;
    else if (t === 'elevated') elevated++;
    else if (t === 'high') high++;
  }
  const n = reported.length || 1;

  const seg = (count: number, color: string) =>
    count > 0 ? <span style={{ flex: count, background: color }} /> : null;

  return (
    <section className="card" data-tour="snapshot">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
        <p className="eyebrow" style={{ marginBottom: 4 }}>Your snapshot</p>
        <span className="caption">{reported.length} of {total} reported</span>
      </div>
      <h2 className="display" style={{ fontSize: 26, marginBottom: 4 }}>
        {reported.length} {reported.length === 1 ? 'marker' : 'markers'} to review
      </h2>
      <p className="caption" style={{ marginBottom: 14 }}>
        {inRange} in range · {elevated} elevated · {high} high
      </p>

      {/* segmented distribution bar */}
      <div style={{ display: 'flex', height: 8, borderRadius: 999, overflow: 'hidden', gap: 2 }}>
        {seg(inRange, 'var(--in-range)')}
        {seg(elevated, 'var(--elevated)')}
        {seg(high, 'var(--high)')}
        {reported.length === 0 && <span style={{ flex: 1, background: 'var(--surface-sunken)' }} />}
      </div>

      {/* legend */}
      <div style={{ display: 'flex', gap: 18, marginTop: 12, flexWrap: 'wrap' }}>
        {[['In range', inRange, 'var(--in-range)'],
          ['Elevated', elevated, 'var(--elevated)'],
          ['High', high, 'var(--high)']].map(([label, count, color]) => (
          <span key={label as string} style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 12.5 }}>
            <span style={{ width: 8, height: 8, borderRadius: 999, background: color as string }} />
            <strong className="num" style={{ color: 'var(--ink)' }}>{count}</strong>
            <span style={{ color: 'var(--ink-soft)' }}>{label}</span>
          </span>
        ))}
      </div>
    </section>
  );
}
