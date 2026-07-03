'use client';
/**
 * frontend/src/components/MetricRangeBar.tsx
 * Compact horizontal range bar: guideline zones (in-range / elevated / high) with
 * the patient's value as a needle and the cohort median as a hollow benchmark ring.
 * The needle colour follows the server-computed status tone — zones are context.
 */
import type { ChipTone } from '@/lib/categoryStyles';
import { BIOMARKER_SCALE, TONE_COLOR } from '@/lib/biomarkerScale';

function clampPct(v: number, min: number, max: number): number {
  if (max === min) return 50;
  return Math.max(2, Math.min(98, ((v - min) / (max - min)) * 100));
}

interface Props {
  biomarker: string;
  value: number;
  tone: ChipTone;
  benchmark?: number | null;
}

export function MetricRangeBar({ biomarker, value, tone, benchmark }: Props) {
  const scale = BIOMARKER_SCALE[biomarker];
  if (!scale) return null;

  const { min, max, zones } = scale;
  const markerLeft = clampPct(value, min, max);
  const hasBench = benchmark !== null && benchmark !== undefined;
  const benchLeft = hasBench ? clampPct(benchmark as number, min, max) : 0;
  const markerColor = TONE_COLOR[tone] ?? 'var(--ink)';

  return (
    <div style={{ position: 'relative', height: 10, margin: '14px 0 9px' }}>
      <div style={{ display: 'flex', height: 10, borderRadius: 999, overflow: 'hidden' }}>
        {zones.map((z, i) => {
          const from = i === 0 ? min : zones[i - 1].to;
          const w = ((z.to - from) / (max - min)) * 100;
          return <div key={i} style={{ width: `${w}%`, background: TONE_COLOR[z.tone], opacity: 0.5 }} />;
        })}
      </div>

      {hasBench && (
        <div
          title={`Benchmark median ${benchmark}`}
          style={{
            position: 'absolute', top: '50%', left: `${benchLeft}%`,
            width: 11, height: 11, borderRadius: 999,
            border: '2px solid var(--ink-faint)', background: 'var(--surface)',
            transform: 'translate(-50%, -50%)', boxSizing: 'border-box',
          }}
        />
      )}

      <div
        title={`You ${value}`}
        style={{
          position: 'absolute', top: '50%', left: `${markerLeft}%`,
          width: 4, height: 20, borderRadius: 999, background: markerColor,
          transform: 'translate(-50%, -50%)',
          boxShadow: '0 0 0 3px var(--surface), 0 1px 3px rgba(24,34,47,0.28)',
        }}
      />
    </div>
  );
}
