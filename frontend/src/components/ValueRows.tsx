'use client';
/**
 * frontend/src/components/ValueRows.tsx
 * The unified results list: one row per value showing the number, its guideline
 * category chip, and the patient's position within the reference distribution
 * (the peer-comparison bar) right beside it. Advanced markers (ApoB, Lp(a)) are
 * appended as classification-only rows (no benchmark bar).
 *
 * The bar is the neutral cohort distribution (p10–p90, p25–p75 emphasized) with
 * the patient's marker colored by clinical status. We intentionally do NOT paint
 * "good/bad" zones because directionality differs by biomarker (e.g. higher HDL
 * is better) — the category chip carries the clinical read, the bar carries the
 * peer position. Reference labeled exactly (never described as South Asian when
 * it is the NHANES cohort).
 */
import type { BenchmarkPoint, BenchmarkResponse, ThresholdResult } from '@/lib/types';
import { BIOMARKER_NAME } from '@/lib/biomarkerMeta';
import { toneColor } from '@/lib/categoryStyles';

function norm(v: number, lo: number, hi: number): number {
  if (hi === lo) return 50;
  return Math.max(0, Math.min(100, ((v - lo) / (hi - lo)) * 100));
}

function percentileLabel(value: number, b: BenchmarkPoint): string {
  const a: [number, number][] = [
    [b.cohort_p10, 10], [b.cohort_p25, 25], [b.cohort_median, 50],
    [b.cohort_p75, 75], [b.cohort_p90, 90],
  ];
  if (value <= a[0][0]) return '<10th pct';
  if (value >= a[4][0]) return '>90th pct';
  for (let i = 0; i < a.length - 1; i++) {
    const [vlo, plo] = a[i], [vhi, phi] = a[i + 1];
    if (value >= vlo && value <= vhi) {
      const frac = vhi === vlo ? 0 : (value - vlo) / (vhi - vlo);
      return `${Math.round(plo + frac * (phi - plo))}th pct`;
    }
  }
  return '';
}

function PeerBar({ b, color }: { b: BenchmarkPoint; color: string }) {
  const span = (b.cohort_p90 - b.cohort_p10) || 1;
  const lo = b.cohort_p10 - span * 0.18, hi = b.cohort_p90 + span * 0.18;
  const p10 = norm(b.cohort_p10, lo, hi), p25 = norm(b.cohort_p25, lo, hi);
  const p75 = norm(b.cohort_p75, lo, hi), p90 = norm(b.cohort_p90, lo, hi);
  const med = norm(b.cohort_median, lo, hi);
  const has = b.patient_value !== null && b.patient_value !== undefined;
  const px = has ? norm(b.patient_value as number, lo, hi) : 0;
  return (
    <div>
      <div style={{ position: 'relative', height: 14 }}>
        <div style={{ position: 'absolute', top: 5, left: 0, right: 0, height: 4, borderRadius: 2, background: 'var(--surface-sunken)' }} />
        <div style={{ position: 'absolute', top: 5, height: 4, borderRadius: 2, left: `${p10}%`, width: `${p90 - p10}%`, background: 'var(--hairline)' }} />
        <div style={{ position: 'absolute', top: 3, height: 8, borderRadius: 4, left: `${p25}%`, width: `${p75 - p25}%`, background: color, opacity: 0.30 }} />
        <div style={{ position: 'absolute', top: 1, height: 12, width: 1.5, left: `${med}%`, background: 'var(--ink-faint)' }} />
        {has && (
          <div title={`You: ${b.patient_value}`} style={{
            position: 'absolute', top: 0, height: 14, width: 14, borderRadius: '50%',
            left: `calc(${px}% - 7px)`, background: color,
            border: '2.5px solid var(--surface)', boxShadow: 'var(--shadow-1)',
          }} />
        )}
      </div>
      <div className="caption num" style={{ marginTop: 5 }}>
        {has ? `${percentileLabel(b.patient_value as number, b)} · median ${b.cohort_median} · n=${b.cohort_n}`
             : `not provided · median ${b.cohort_median} · n=${b.cohort_n}`}
      </div>
    </div>
  );
}

function Row({ r, bench }: { r: ThresholdResult; bench?: BenchmarkPoint }) {
  const missing = r.category === null;
  return (
    <div style={{
      display: 'grid', gridTemplateColumns: '116px 138px 1fr', alignItems: 'center', gap: 12,
      border: '1px solid var(--hairline)', borderRadius: 'var(--radius-sm)', padding: '12px 14px',
      opacity: missing ? 0.72 : 1,
    }}>
      <div>
        <span className="num" style={{ fontSize: 19, fontWeight: 600, color: 'var(--ink)' }}>
          {missing ? '—' : r.value}
        </span>
        <span className="caption" style={{ marginLeft: 4 }}>{r.unit}</span>
        <div className="caption" style={{ marginTop: 2 }}>{BIOMARKER_NAME[r.biomarker] ?? r.biomarker}</div>
      </div>
      <span style={{
        justifySelf: 'center', textAlign: 'center', fontSize: 12.5, fontWeight: 600,
        color: toneColor(r.category),
      }}>
        {missing ? 'Not provided' : r.category}
      </span>
      <div>
        {bench ? <PeerBar b={bench} color={toneColor(r.category)} />
               : <span className="caption">{r.guideline_source}</span>}
      </div>
    </div>
  );
}

export function ValueRows({ result }: { result: BenchmarkResponse }) {
  const benchByKey = new Map(result.benchmark_data.map((b) => [b.biomarker, b]));
  const matched = result.matched && result.match_description;
  return (
    <section className="card">
      <p className="eyebrow" style={{ marginBottom: 4 }}>Your values</p>
      <h2 className="title" style={{ marginBottom: 4 }}>Each value, beside your peers</h2>
      <p className="caption" style={{ marginBottom: 16 }}>
        vs {matched ? `matched peers — ${result.match_description}` : result.cohort_label}
      </p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {result.threshold_results.map((r) => (
          <Row key={r.biomarker} r={r} bench={benchByKey.get(r.biomarker)} />
        ))}
        {result.risk_enhancing_markers.map((r) => (
          <Row key={r.biomarker} r={r} />
        ))}
      </div>

      {result.risk_enhancing_markers.length > 0 && (
        <p className="caption" style={{ marginTop: 12 }}>
          ApoB and Lp(a) are guideline-classified risk-enhancing factors, shown without a
          population bar (the reference cohorts do not measure them).
        </p>
      )}
    </section>
  );
}
