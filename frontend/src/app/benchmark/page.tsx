'use client';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import type { BiomarkerInput, BenchmarkResponse, CohortId } from '@/lib/types';
import { COHORT_LABELS } from '@/lib/types';
import { submitBiomarkers } from '@/lib/api';
import { BiomarkerForm } from '@/components/BiomarkerForm';

// Educational example profiles — synthetic, not real patients. Let a visitor or
// reviewer see a populated result instantly instead of typing values.
const EXAMPLES: Record<string, { label: string; values: Partial<BiomarkerInput> }> = {
  elevated: {
    label: 'Elevated-risk example',
    values: {
      LDL_mgdl: 168, HDL_mgdl: 40, TG_mgdl: 210, TC_mgdl: 240,
      FPG_mgdl: 112, fasting_status: 'confirmed', HbA1c_pct: 6.1,
      SBP_mmhg: 136, DBP_mmhg: 86,
      BMI_kgm2: 27.0, age_yr: 52, sex: 'M', south_asian: true,
      chol_med: false, bp_med: false, insulin: false, dm_pills: false,
    },
  },
  healthy: {
    label: 'In-range example',
    values: {
      LDL_mgdl: 92, HDL_mgdl: 62, TG_mgdl: 90, TC_mgdl: 170,
      FPG_mgdl: 88, fasting_status: 'confirmed', HbA1c_pct: 5.2,
      SBP_mmhg: 112, DBP_mmhg: 72,
      BMI_kgm2: 22.0, age_yr: 41, sex: 'F', south_asian: true,
      chol_med: false, bp_med: false, insulin: false, dm_pills: false,
    },
  },
};

export default function BenchmarkPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [seed, setSeed] = useState<Partial<BiomarkerInput> | undefined>(undefined);
  const [formKey, setFormKey] = useState(0);
  const [cohort, setCohort] = useState<CohortId>('nhanes_asian');
  const [match, setMatch] = useState(false);

  // Re-seed the form when returning from results via "Adjust".
  useEffect(() => {
    const stored = sessionStorage.getItem('benchmarkInput');
    if (stored) {
      try {
        setSeed(JSON.parse(stored) as Partial<BiomarkerInput>);
        setFormKey((k) => k + 1);
      } catch { /* ignore malformed cache */ }
    }
  }, []);

  function loadExample(key: keyof typeof EXAMPLES) {
    setSeed(EXAMPLES[key].values);
    setFormKey((k) => k + 1);   // remount the form with seeded values
  }

  async function handleSubmit(input: BiomarkerInput) {
    setIsLoading(true);
    setError(null);
    try {
      const result: BenchmarkResponse = await submitBiomarkers(input, cohort, match);
      sessionStorage.setItem('benchmarkResult', JSON.stringify(result));
      sessionStorage.setItem('benchmarkInput', JSON.stringify(input));
      router.push('/results');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 'calc(var(--content-w, 880px) - 160px)', margin: '0 auto', padding: '32px 24px' }}>
      <div style={{ marginBottom: 24 }}>
        <p className="eyebrow" style={{ marginBottom: 4 }}>Biomarker Input</p>
        <h1 className="display">Enter Your Lab Values</h1>
        <p className="body" style={{ marginTop: 8 }}>
          Every field is optional — anything you leave blank is simply flagged as
          not provided. No data is stored beyond this browser session.
        </p>
      </div>

      {/* Cohort + peer-matching controls. Both flow straight through to the API
          (?cohort=&match=) — see frontend/src/lib/api.ts submitBiomarkers. */}
      <div className="panel-sunken" style={{
        display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap', marginBottom: 20,
      }}>
        <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span className="caption" style={{ fontWeight: 600 }}>Compare against:</span>
          <select className="input" style={{ maxWidth: 280 }} value={cohort}
            onChange={(e) => setCohort(e.target.value as CohortId)}>
            <option value="nhanes_asian">{COHORT_LABELS.nhanes_asian}</option>
            <option value="sahc">{COHORT_LABELS.sahc}</option>
          </select>
        </label>
        <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}
          title="Narrow the benchmark to a matched peer subgroup (sex + age band + medication use). Small cells are suppressed and disclosed. NHANES falls back to the whole-cohort distribution — peer matching is only available on the SAHC cohort.">
          <input type="checkbox" checked={match} onChange={(e) => setMatch(e.target.checked)} />
          <span className="caption">Match to peers (sex, age, medications)</span>
        </label>
      </div>

      {/* Example data — for demos and first-time visitors */}
      <div data-tour="examples" className="panel-sunken" style={{
        display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap', marginBottom: 20,
      }}>
        <span className="caption" style={{ fontWeight: 600 }}>New here? Try an example:</span>
        {(Object.keys(EXAMPLES) as (keyof typeof EXAMPLES)[]).map((k) => (
          <button key={k} className="btn btn-outline" style={{ height: 34, fontSize: 13 }}
            onClick={() => loadExample(k)}>
            {EXAMPLES[k].label}
          </button>
        ))}
      </div>

      <div data-tour="form">
        <BiomarkerForm key={formKey} onSubmit={handleSubmit} isLoading={isLoading} initialValues={seed} />
      </div>

      {error && (
        <div role="alert" style={{
          marginTop: 16, padding: '12px 16px', borderRadius: 8,
          backgroundColor: 'var(--high-tint)', color: '#410E0B', fontSize: 13,
        }}>
          {error}
        </div>
      )}
    </div>
  );
}
