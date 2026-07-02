'use client';
/**
 * frontend/src/components/BenchmarkBar.tsx
 * Daylight-style horizontal bar showing the patient's value ("You") against the
 * population benchmark median, colored by the value's clinical status tone and
 * the biomarker group. Presentation only — all numbers come from the API.
 */
interface Props {
  value: number | null;
  benchmark: number | null;      // cohort median
  low: number;                   // display-scale lower bound
  high: number;                  // display-scale upper bound
  tone: 'normal' | 'elevated' | 'high' | 'missing';
  group: string;                 // grp-lipids | grp-glucose | grp-bp | grp-body
  unit?: string;
}

const TONE_VAR: Record<string, string> = {
  normal: 'var(--in-range)',
  elevated: 'var(--elevated)',
  high: 'var(--high)',
  missing: 'var(--missing)',
};

function pct(v: number, lo: number, hi: number): number {
  if (hi === lo) return 50;
  return Math.max(2, Math.min(98, ((v - lo) / (hi - lo)) * 100));
}

export function BenchmarkBar({ value, benchmark, low, high, tone, group, unit }: Props) {
  const hasValue = value !== null && value !== undefined;
  const hasBench = benchmark !== null && benchmark !== undefined;
  const youX = hasValue ? pct(value as number, low, high) : 0;
  const benchX = hasBench ? pct(benchmark as number, low, high) : 0;

  return (
    <div style={{ marginTop: 12 }}>
      <div style={{ position: 'relative', height: 10 }}>
        {/* track */}
        <div style={{
          position: 'absolute', top: 3, left: 0, right: 0, height: 4,
          borderRadius: 999, background: 'var(--surface-sunken)',
        }} />
        {/* group-tinted fill up to the patient value */}
        {hasValue && (
          <div style={{
            position: 'absolute', top: 3, left: 0, width: `${youX}%`, height: 4,
            borderRadius: 999, background: `var(--${group})`, opacity: 0.35,
          }} />
        )}
        {/* benchmark median marker (hollow ring) */}
        {hasBench && (
          <div title={`Benchmark ${benchmark}`} style={{
            position: 'absolute', top: 0, left: `calc(${benchX}% - 5px)`,
            width: 10, height: 10, borderRadius: 999,
            border: '1.5px solid var(--ink-faint)', background: 'var(--surface)',
            boxSizing: 'border-box',
          }} />
        )}
        {/* patient marker (filled, tone-colored) */}
        {hasValue && (
          <div title={`You ${value}`} style={{
            position: 'absolute', top: 0, left: `calc(${youX}% - 5px)`,
            width: 10, height: 10, borderRadius: 3, background: TONE_VAR[tone],
            boxShadow: 'var(--shadow-1)',
          }} />
        )}
      </div>
      {/* legend row */}
      <div style={{
        display: 'flex', justifyContent: 'space-between', marginTop: 8,
        fontSize: 10.5, color: 'var(--ink-faint)',
      }}>
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5 }}>
          <span style={{ width: 7, height: 7, borderRadius: 2, background: TONE_VAR[tone] }} />
          You {hasValue ? value : '—'}
        </span>
        {hasBench && (
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5 }}>
            <span style={{
              width: 8, height: 8, borderRadius: 999,
              border: '1.5px solid var(--ink-faint)', boxSizing: 'border-box',
            }} />
            Benchmark {benchmark}
          </span>
        )}
      </div>
    </div>
  );
}
