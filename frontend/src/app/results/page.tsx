'use client';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import type { BenchmarkResponse } from '@/lib/types';
import { ThresholdCards } from '@/components/ThresholdCards';
import { DistributionChart } from '@/components/DistributionChart';
import { SouthAsianContextPanel } from '@/components/SouthAsianContextPanel';
import { MedicationNotes } from '@/components/MedicationNotes';
import { PhysicianGuide } from '@/components/PhysicianGuide';
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
    <div style={{ maxWidth: 840, margin: '0 auto', padding: '24px',
      display: 'flex', flexDirection: 'column', gap: 16 }}>

      {/* Disclaimer — always first, always rendered, verbatim from API */}
      <div style={{
        padding: '12px 16px', borderRadius: 8, fontSize: 13,
        backgroundColor: '#FFF8E1', color: '#E65100', border: '1px solid #FFE082',
      }}>
        {result.disclaimer}
      </div>

      {/* Cohort + validation badges */}
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
        <span className="chip chip-primary">{result.cohort_label}</span>
        <span style={{
          padding: '4px 10px', borderRadius: 20, fontSize: 11,
          backgroundColor: 'var(--panel-sunken)', color: 'var(--ink-soft)',
        }}>
          {result.validation_status}
        </span>
      </div>

      <ThresholdCards results={result.threshold_results} missingBiomarkers={result.missing_biomarkers} />
      <DistributionChart benchmarkData={result.benchmark_data} cohortLabel={result.cohort_label} />
      <SouthAsianContextPanel items={result.south_asian_context} />
      <MedicationNotes notes={result.medication_notes} />
      <PhysicianGuide items={result.physician_guide} />
      <LimitationsPanel />

      <div style={{ display: 'flex', justifyContent: 'center', paddingTop: 8 }}>
        <Link href="/benchmark" className="btn btn-text">Start Over</Link>
      </div>
    </div>
  );
}
