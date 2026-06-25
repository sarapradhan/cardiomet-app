'use client';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import type { BenchmarkResponse } from '@/lib/types';
import { ValueRows } from '@/components/ValueRows';
import { Legend } from '@/components/Legend';
import { SouthAsianContextPanel } from '@/components/SouthAsianContextPanel';
import { MedicationNotes } from '@/components/MedicationNotes';
import { PhysicianGuide } from '@/components/PhysicianGuide';
import { ClinicianBrief } from '@/components/ClinicianBrief';
import { CareNavigation } from '@/components/CareNavigation';
import { LimitationsPanel } from '@/components/LimitationsPanel';

export default function ResultsPage() {
  const [result, setResult] = useState<BenchmarkResponse | null>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const stored = sessionStorage.getItem('benchmarkResult');
    if (stored) {
      try { setResult(JSON.parse(stored) as BenchmarkResponse); }
      catch { sessionStorage.removeItem('benchmarkResult'); }
    }
    setLoaded(true);
  }, []);

  if (loaded && !result) {
    return (
      <div style={{ maxWidth: 480, margin: '64px auto', padding: '0 24px', textAlign: 'center' }}>
        <div className="card">
          <p className="body" style={{ marginBottom: 20 }}>No results to show yet.</p>
          <Link href="/benchmark" className="btn btn-outline">Enter Biomarkers</Link>
        </div>
      </div>
    );
  }

  if (!result) return null;

  return (
    <div style={{ maxWidth: 1180, margin: '0 auto', padding: '24px',
      display: 'flex', flexDirection: 'column', gap: 16 }}>

      {/* Disclaimer — always first, always rendered, verbatim from API */}
      <div style={{
        padding: '12px 16px', borderRadius: 8, fontSize: 13,
        backgroundColor: '#FFF8E1', color: '#E65100', border: '1px solid #FFE082',
      }}>
        {result.disclaimer}
      </div>

      {/* Hero — serif headline with cohort + matched badges */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', gap: 16, flexWrap: 'wrap' }}>
        <div>
          <p className="eyebrow" style={{ marginBottom: 6 }}>Your results · South Asian cardiometabolic health</p>
          <h1 className="display" style={{ fontSize: 30 }}>Your numbers, in context.</h1>
        </div>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
          <span className="chip chip-primary">{result.cohort_label}</span>
          {result.matched && result.match_description && (
            <span className="chip chip-primary" title="Compared against a matched peer subgroup">
              Matched: {result.match_description}
            </span>
          )}
          <span style={{
            padding: '4px 10px', borderRadius: 20, fontSize: 11,
            backgroundColor: 'var(--panel-sunken)', color: 'var(--ink-soft)',
          }}>
            {result.validation_status}
          </span>
        </div>
      </div>

      <Legend />

      {/* At-a-glance summary strip */}
      <ResultsSummary result={result} />

      {/* Landscape two-column body: values + peers on the left, context rail right */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 items-start">
        <div className="lg:col-span-2 flex flex-col gap-4">
          <ValueRows result={result} />
          <PhysicianGuide items={result.physician_guide} />
        </div>
        <div className="flex flex-col gap-4">
          <SouthAsianContextPanel items={result.south_asian_context} />
          <MedicationNotes notes={result.medication_notes} />
          <CareNavigation items={result.care_navigation} />
          <ClinicianBrief result={result} />
        </div>
      </div>

      <LimitationsPanel />

      <div style={{ display: 'flex', justifyContent: 'center', paddingTop: 8 }}>
        <Link href="/benchmark" className="btn btn-text">Start Over</Link>
      </div>
    </div>
  );
}

const _NORMAL = new Set(['Optimal', 'Near Optimal', 'Normal', 'Desirable', 'Protective', 'Within range']);

function ResultsSummary({ result }: { result: BenchmarkResponse }) {
  const provided = result.threshold_results.filter((r) => r.category !== null);
  const outOfRange = provided.filter((r) => !_NORMAL.has(r.category as string)).length;
  const inRange = provided.length - outOfRange;
  const tile = {
    background: 'var(--surface)', border: '1px solid var(--hairline)',
    borderRadius: 'var(--radius-sm)', padding: '14px 16px',
  } as const;
  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <div style={tile}>
        <div className="num" style={{ fontSize: 26, fontWeight: 600, color: 'var(--high)' }}>{outOfRange}</div>
        <div className="caption">out of range</div>
      </div>
      <div style={tile}>
        <div className="num" style={{ fontSize: 26, fontWeight: 600, color: 'var(--in-range)' }}>{inRange}</div>
        <div className="caption">in range</div>
      </div>
      <div style={{ ...tile, gridColumn: 'span 2' }}>
        <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--primary)' }}>Compared against</div>
        <div className="caption" style={{ marginTop: 2 }}>
          {result.matched && result.match_description
            ? `${result.cohort_label} · ${result.match_description}`
            : result.cohort_label}
        </div>
      </div>
    </div>
  );
}
