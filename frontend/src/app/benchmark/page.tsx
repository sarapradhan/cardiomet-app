'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import type { BiomarkerInput, BenchmarkResponse, CohortId } from '@/lib/types';
import { submitBiomarkers } from '@/lib/api';
import { BiomarkerForm } from '@/components/BiomarkerForm';

// Selectable reference cohorts. Labels are honest to each cohort: NHANES is a
// US population proxy; SAHC is a genuine South Asian clinical cohort.
const COHORT_OPTIONS: { id: CohortId; short: string; label: string; blurb: string }[] = [
  {
    id: 'nhanes_asian',
    short: 'NHANES',
    label: 'NHANES Non-Hispanic Asian',
    blurb: 'US national survey, Non-Hispanic Asian adults (2017–2018). A public, reproducible population proxy.',
  },
  {
    id: 'sahc',
    short: 'SAHC cohort',
    label: 'South Asian Heart Center cohort',
    blurb: 'De-identified South Asian clinic patients — South Asian–specific distributions (e.g. lower HDL, higher triglycerides).',
  },
];

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
  const [cohort, setCohort] = useState<CohortId>('nhanes_asian');
  const [match, setMatch] = useState(false);

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
      router.push('/results');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 1120, margin: '0 auto', padding: '32px 24px' }}>
      <div style={{ marginBottom: 24 }}>
        <p className="eyebrow" style={{ marginBottom: 4 }}>Biomarker Input</p>
        <h1 className="display">Enter Your Lab Values</h1>
        <p className="body" style={{ marginTop: 8 }}>
          Every field is optional — anything you leave blank is simply flagged as
          not provided. No data is stored beyond this browser session.
        </p>
      </div>

      {/* Landscape two-column: lab form left, options rail right */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5 items-start">
        <div data-tour="form" className="lg:col-span-2">
          <BiomarkerForm key={formKey} onSubmit={handleSubmit} isLoading={isLoading} initialValues={seed} />
        </div>

        <div className="flex flex-col gap-4">
          {/* Example data — for demos and first-time visitors */}
          <div data-tour="examples" className="panel-sunken" style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            <span className="caption" style={{ fontWeight: 600 }}>New here? Try an example:</span>
            <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
              {(Object.keys(EXAMPLES) as (keyof typeof EXAMPLES)[]).map((k) => (
                <button key={k} className="btn btn-outline" style={{ height: 34, fontSize: 13 }}
                  onClick={() => loadExample(k)}>
                  {EXAMPLES[k].label}
                </button>
              ))}
            </div>
          </div>

          {/* Reference cohort selector — compact segmented control + caption */}
          <div data-tour="cohort" className="panel-sunken" style={{ padding: 16 }}>
            <span className="caption" style={{ fontWeight: 600 }}>Compare against</span>
            <div role="group" aria-label="Reference cohort" style={{
              display: 'flex', marginTop: 10, border: '1px solid var(--hairline)',
              borderRadius: 999, overflow: 'hidden', background: 'var(--surface)',
            }}>
              {COHORT_OPTIONS.map((opt) => {
                const selected = cohort === opt.id;
                return (
                  <button
                    key={opt.id}
                    type="button"
                    aria-pressed={selected}
                    onClick={() => setCohort(opt.id)}
                    style={{
                      flex: 1, height: 34, border: 'none', cursor: 'pointer',
                      fontSize: 12.5, fontWeight: 550, whiteSpace: 'nowrap',
                      background: selected ? 'var(--primary)' : 'transparent',
                      color: selected ? 'var(--on-primary)' : 'var(--primary)',
                    }}
                  >
                    {opt.short}
                  </button>
                );
              })}
            </div>
            <p className="caption" style={{ marginTop: 8, lineHeight: 1.5 }}>
              {COHORT_OPTIONS.find((o) => o.id === cohort)?.blurb}
            </p>

            {/* Peer matching — SCORE-style: match the comparison group to the patient */}
            <label style={{ display: 'flex', gap: 10, alignItems: 'flex-start', marginTop: 14, cursor: 'pointer' }}>
              <input type="checkbox" checked={match} onChange={(e) => setMatch(e.target.checked)}
                style={{ marginTop: 3 }} />
              <span>
                <span style={{ fontWeight: 600, fontSize: 13 }}>Match to people like me</span>
                <span style={{ display: 'block', fontSize: 11, color: 'var(--ink-soft)', marginTop: 2 }}>
                  Compare against peers of the same sex, age range, and medication use (requires age
                  and sex). Available for the South Asian Heart Center cohort; if a peer group is too
                  small it falls back to the full cohort and says so.
                </span>
              </span>
            </label>
          </div>
        </div>
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
