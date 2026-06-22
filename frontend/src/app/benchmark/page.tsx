'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import type { BiomarkerInput, BenchmarkResponse } from '@/lib/types';
import { submitBiomarkers } from '@/lib/api';
import { BiomarkerForm } from '@/components/BiomarkerForm';

// Educational example profiles — synthetic, not real patients. Let a visitor or
// reviewer see a populated result instantly instead of typing values.
const EXAMPLES: Record<string, { label: string; values: Partial<BiomarkerInput> }> = {
  elevated: {
    label: 'Elevated-risk example',
    values: {
      LDL_mgdl: 168, HDL_mgdl: 40, TG_mgdl: 210, TC_mgdl: 240,
      FPG_mgdl: 112, HbA1c_pct: 6.1, SBP_mmhg: 136, DBP_mmhg: 86,
      BMI_kgm2: 27.0, age_yr: 52, sex: 'M', south_asian: true,
      chol_med: false, bp_med: false, insulin: false, dm_pills: false,
    },
  },
  healthy: {
    label: 'In-range example',
    values: {
      LDL_mgdl: 92, HDL_mgdl: 62, TG_mgdl: 90, TC_mgdl: 170,
      FPG_mgdl: 88, HbA1c_pct: 5.2, SBP_mmhg: 112, DBP_mmhg: 72,
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

  function loadExample(key: keyof typeof EXAMPLES) {
    setSeed(EXAMPLES[key].values);
    setFormKey((k) => k + 1);   // remount the form with seeded values
  }

  async function handleSubmit(input: BiomarkerInput) {
    setIsLoading(true);
    setError(null);
    try {
      const result: BenchmarkResponse = await submitBiomarkers(input);
      sessionStorage.setItem('benchmarkResult', JSON.stringify(result));
      router.push('/results');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 720, margin: '0 auto', padding: '32px 24px' }}>
      <div style={{ marginBottom: 24 }}>
        <p className="eyebrow" style={{ marginBottom: 4 }}>Biomarker Input</p>
        <h1 className="display">Enter Your Lab Values</h1>
        <p className="body" style={{ marginTop: 8 }}>
          Every field is optional — anything you leave blank is simply flagged as
          not provided. No data is stored beyond this browser session.
        </p>
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
