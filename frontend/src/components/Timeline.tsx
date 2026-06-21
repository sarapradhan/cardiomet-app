'use client';
/**
 * frontend/src/components/Timeline.tsx
 * Small-multiples timeline: one compact SVG sparkline per biomarker over time,
 * with the patient's points plotted, the line colored by the latest category
 * tone, and intervention markers on the date axis. Pure presentation — all
 * values and categories come from the API. No clinical logic here.
 */
import type { BiomarkerTrajectory, InterventionMarker } from '@/lib/types';

interface Props {
  trajectories: BiomarkerTrajectory[];
  interventions: InterventionMarker[];
}

const TONE_COLOR: Record<string, string> = {
  normal: 'var(--primary)',
  elevated: '#E65100',
  high: '#B71C1C',
  missing: 'var(--ink-faint)',
};

const W = 260;
const H = 64;
const PAD = 8;

function Sparkline({ t, interventionDates }: { t: BiomarkerTrajectory; interventionDates: number[] }) {
  const present = t.points.filter((p) => p.value !== null) as { draw_date: string; value: number; category_tone: string }[];
  const allDates = t.points.map((p) => new Date(p.draw_date).getTime());
  const minT = Math.min(...allDates);
  const maxT = Math.max(...allDates);
  const tSpan = maxT - minT || 1;

  const vals = present.map((p) => p.value);
  const vMin = vals.length ? Math.min(...vals) : 0;
  const vMax = vals.length ? Math.max(...vals) : 1;
  const vSpan = vMax - vMin || 1;

  const x = (ts: number) => PAD + ((ts - minT) / tSpan) * (W - 2 * PAD);
  const y = (v: number) => H - PAD - ((v - vMin) / vSpan) * (H - 2 * PAD);

  const lineColor = TONE_COLOR[present.at(-1)?.category_tone ?? 'missing'] ?? 'var(--ink-faint)';
  const path = present
    .map((p, i) => `${i === 0 ? 'M' : 'L'} ${x(new Date(p.draw_date).getTime()).toFixed(1)} ${y(p.value).toFixed(1)}`)
    .join(' ');

  return (
    <svg viewBox={`0 0 ${W} ${H}`} width="100%" style={{ display: 'block' }} role="img"
      aria-label={`${t.biomarker} trend`}>
      {/* intervention markers (vertical guides) */}
      {interventionDates.map((ts, i) => (
        <line key={i} x1={x(ts)} x2={x(ts)} y1={PAD / 2} y2={H - PAD / 2}
          stroke="var(--primary)" strokeWidth={1} strokeDasharray="2 2" opacity={0.6} />
      ))}
      {/* trend line */}
      {present.length >= 2 && <path d={path} fill="none" stroke={lineColor} strokeWidth={2} />}
      {/* points */}
      {present.map((p, i) => (
        <circle key={i} cx={x(new Date(p.draw_date).getTime())} cy={y(p.value)} r={3.5}
          fill={TONE_COLOR[p.category_tone] ?? lineColor} stroke="#fff" strokeWidth={1} />
      ))}
      {present.length === 0 && (
        <text x={W / 2} y={H / 2} textAnchor="middle" fontSize="11" fill="var(--ink-soft)">
          no data
        </text>
      )}
    </svg>
  );
}

export function Timeline({ trajectories, interventions }: Props) {
  const interventionTs = interventions.map((iv) => new Date(iv.draw_date).getTime());

  return (
    <section className="card" style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
      <p className="eyebrow" style={{ marginBottom: 4 }}>Timeline</p>
      <h2 className="title" style={{ marginBottom: 4 }}>Your Values Over Time</h2>
      <p className="body" style={{ marginBottom: 16 }}>
        Each line shows one biomarker across your draws. Dashed guides mark when a
        medication was started. Point color reflects the guideline category.
      </p>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 16 }}>
        {trajectories.map((t) => {
          const latest = t.points.filter((p) => p.value !== null).at(-1);
          return (
            <div key={t.biomarker} className="panel-sunken"
              style={{ display: 'flex', flexDirection: 'column', gap: 4, padding: 12 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
                <span style={{ fontSize: 13, fontWeight: 600 }}>{t.biomarker}</span>
                <span style={{ fontSize: 11, color: 'var(--ink-soft)' }}>
                  {latest ? `${latest.value} ${t.unit}` : '—'}
                </span>
              </div>
              <Sparkline t={t} interventionDates={interventionTs} />
              <span style={{ fontSize: 11, color: 'var(--ink-soft)' }}>
                {t.direction === 'insufficient_data'
                  ? 'Need ≥2 dated values'
                  : `${t.direction}${t.change_absolute !== null ? ` · Δ ${t.change_absolute} ${t.unit}` : ''}`}
              </span>
            </div>
          );
        })}
      </div>
    </section>
  );
}
