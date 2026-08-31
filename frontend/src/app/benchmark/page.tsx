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
  // Held as state rather than inlined at the call site: the cohort selector and
  // peer-matching toggle were removed on 2026-08-30 (see the panel below), but
  // both remain live API parameters, so this is where a restored control would
  // reattach.
  const [cohort] = useState<CohortId>('nhanes_asian');
  const [match] = useState(false);

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

      {/* Benchmark cohort.

          Two controls used to live here: a cohort selector and a "Match to
          peers" toggle. Both were removed on 2026-08-30.

          - The selector offered a second cohort ("sahc") whose provenance could
            not be established; that cohort was removed (docs/SAHC_COHORT.md).
            With one registered cohort a selector would be a control with one
            option, so the cohort is stated instead of chosen.
          - Peer matching was only ever available on that cohort. Leaving the
            toggle would render a control that silently does nothing, which is
            the class of problem this cleanup exists to remove.

          Both still flow through the API (?cohort=&match= in
          frontend/src/lib/api.ts), and the engine behind them is intact, so
          restoring these controls when a sourced cohort is registered is a UI
          change only. */}
      <div className="panel-sunken" style={{
        display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap', marginBottom: 20,
      }}>
        <span className="caption" style={{ fontWeight: 600 }}>Compared against:</span>
        <span className="caption" data-testid="cohort-name">{COHORT_LABELS.nhanes_asian}</span>
        <span className="caption" style={{ opacity: 0.85 }}>
          &mdash; a public U.S. survey population, used as a proxy. NHANES has no
          South Asian&ndash;specific sample.
        </span>
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
