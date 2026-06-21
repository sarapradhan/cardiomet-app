'use client';
/**
 * frontend/src/components/BiomarkerForm.tsx
 * Material Design input form for biomarker entry. Every clinical field is
 * optional (the API flags anything missing); only sex/ancestry/medication
 * toggles default to a value. Calls onSubmit with a fully-typed BiomarkerInput.
 */
import { useState } from 'react';
import type { BiomarkerInput } from '@/lib/types';

interface NumField {
  key: keyof BiomarkerInput;
  label: string;
  unit: string;
  placeholder: string;
}

const LIPID_FIELDS: NumField[] = [
  { key: 'LDL_mgdl', label: 'LDL Cholesterol', unit: 'mg/dL', placeholder: 'e.g. 100' },
  { key: 'HDL_mgdl', label: 'HDL Cholesterol', unit: 'mg/dL', placeholder: 'e.g. 55' },
  { key: 'TG_mgdl', label: 'Triglycerides', unit: 'mg/dL', placeholder: 'e.g. 120' },
  { key: 'TC_mgdl', label: 'Total Cholesterol', unit: 'mg/dL', placeholder: 'e.g. 185' },
];

const METABOLIC_FIELDS: NumField[] = [
  { key: 'FPG_mgdl', label: 'Fasting Glucose', unit: 'mg/dL', placeholder: 'e.g. 90' },
  { key: 'HbA1c_pct', label: 'HbA1c', unit: '%', placeholder: 'e.g. 5.4' },
];

const VITALS_FIELDS: NumField[] = [
  { key: 'SBP_mmhg', label: 'Systolic BP', unit: 'mm Hg', placeholder: 'e.g. 118' },
  { key: 'DBP_mmhg', label: 'Diastolic BP', unit: 'mm Hg', placeholder: 'e.g. 76' },
  { key: 'BMI_kgm2', label: 'BMI', unit: 'kg/m²', placeholder: 'e.g. 23.5' },
];

const MEDS: { key: keyof BiomarkerInput; label: string }[] = [
  { key: 'chol_med', label: 'Cholesterol medication' },
  { key: 'bp_med', label: 'Blood pressure medication' },
  { key: 'insulin', label: 'Insulin' },
  { key: 'dm_pills', label: 'Diabetes pills' },
];

interface Props {
  onSubmit: (input: BiomarkerInput) => void;
  isLoading?: boolean;
}

export function BiomarkerForm({ onSubmit, isLoading = false }: Props) {
  const [values, setValues] = useState<Record<string, string>>({});
  const [age, setAge] = useState<string>('');
  const [sex, setSex] = useState<'M' | 'F' | ''>('');
  const [southAsian, setSouthAsian] = useState<boolean>(false);
  const [meds, setMeds] = useState<Record<string, boolean>>({
    chol_med: false, bp_med: false, insulin: false, dm_pills: false,
  });

  function setNum(key: string, raw: string) {
    setValues((v) => ({ ...v, [key]: raw }));
  }

  function buildInput(): BiomarkerInput {
    const num = (k: string): number | null => {
      const raw = values[k];
      if (raw === undefined || raw.trim() === '') return null;
      const parsed = Number(raw);
      return Number.isFinite(parsed) ? parsed : null;
    };
    return {
      LDL_mgdl: num('LDL_mgdl'), HDL_mgdl: num('HDL_mgdl'),
      TG_mgdl: num('TG_mgdl'), TC_mgdl: num('TC_mgdl'),
      FPG_mgdl: num('FPG_mgdl'), HbA1c_pct: num('HbA1c_pct'),
      SBP_mmhg: num('SBP_mmhg'), DBP_mmhg: num('DBP_mmhg'),
      BMI_kgm2: num('BMI_kgm2'),
      age_yr: age.trim() === '' ? null : Number(age),
      sex: sex === '' ? null : sex,
      south_asian: southAsian,
      chol_med: meds.chol_med, bp_med: meds.bp_med,
      insulin: meds.insulin, dm_pills: meds.dm_pills,
    };
  }

  function renderGroup(title: string, fields: NumField[]) {
    return (
      <fieldset style={{ border: 'none', margin: 0, padding: 0 }}>
        <legend className="eyebrow" style={{ marginBottom: 12 }}>{title}</legend>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 16 }}>
          {fields.map((f) => (
            <label key={String(f.key)} style={{ display: 'block' }}>
              <span style={{ display: 'block', fontSize: 13, marginBottom: 6, color: 'var(--ink)' }}>
                {f.label} <span style={{ color: 'var(--ink-soft)' }}>({f.unit})</span>
              </span>
              <input
                type="number" inputMode="decimal" step="any"
                className="input" placeholder={f.placeholder}
                value={values[String(f.key)] ?? ''}
                onChange={(e) => setNum(String(f.key), e.target.value)}
              />
            </label>
          ))}
        </div>
      </fieldset>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 28 }}>
      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 28 }}>
        {renderGroup('Lipids', LIPID_FIELDS)}
        <hr className="hairline" />
        {renderGroup('Glucose', METABOLIC_FIELDS)}
        <hr className="hairline" />
        {renderGroup('Vitals & Body', VITALS_FIELDS)}
      </div>

      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
        <fieldset style={{ border: 'none', margin: 0, padding: 0 }}>
          <legend className="eyebrow" style={{ marginBottom: 12 }}>About You</legend>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 16 }}>
            <label style={{ display: 'block' }}>
              <span style={{ display: 'block', fontSize: 13, marginBottom: 6 }}>Age (years)</span>
              <input type="number" inputMode="numeric" className="input" placeholder="e.g. 45"
                value={age} onChange={(e) => setAge(e.target.value)} />
            </label>
            <label style={{ display: 'block' }}>
              <span style={{ display: 'block', fontSize: 13, marginBottom: 6 }}>Sex</span>
              <select className="input" value={sex}
                onChange={(e) => setSex(e.target.value as 'M' | 'F' | '')}>
                <option value="">Select…</option>
                <option value="M">Male</option>
                <option value="F">Female</option>
              </select>
            </label>
          </div>
          <label style={{ display: 'flex', alignItems: 'center', gap: 10, marginTop: 16, cursor: 'pointer' }}>
            <input type="checkbox" checked={southAsian}
              onChange={(e) => setSouthAsian(e.target.checked)} />
            <span style={{ fontSize: 14 }}>South Asian ancestry</span>
          </label>
        </fieldset>

        <hr className="hairline" />

        <fieldset style={{ border: 'none', margin: 0, padding: 0 }}>
          <legend className="eyebrow" style={{ marginBottom: 12 }}>Current Medications</legend>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12 }}>
            {MEDS.map((m) => (
              <label key={String(m.key)} style={{ display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer' }}>
                <input type="checkbox" checked={meds[String(m.key)]}
                  onChange={(e) => setMeds((s) => ({ ...s, [String(m.key)]: e.target.checked }))} />
                <span style={{ fontSize: 14 }}>{m.label}</span>
              </label>
            ))}
          </div>
        </fieldset>
      </div>

      <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
        <button className="btn btn-primary" disabled={isLoading}
          onClick={() => onSubmit(buildInput())}
          style={isLoading ? { opacity: 0.6, cursor: 'not-allowed' } : undefined}>
          {isLoading ? 'Analyzing…' : 'See My Results'}
        </button>
      </div>
    </div>
  );
}
