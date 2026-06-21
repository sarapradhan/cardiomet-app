'use client';
import { useEffect, useRef, useState } from 'react';
import type { BiomarkerInput, BiomarkerDraw, BiomarkerSeries, TrajectoryResponse } from '@/lib/types';
import { submitSeries } from '@/lib/api';
import { BiomarkerForm } from '@/components/BiomarkerForm';
import { Timeline } from '@/components/Timeline';
import { TrajectorySummary } from '@/components/TrajectorySummary';
import { exportHealthFile, parseHealthFile, saveLocal, loadLocal, clearLocal } from '@/lib/healthFile';

export default function TimelinePage() {
  const [draws, setDraws] = useState<BiomarkerDraw[]>([]);
  const [drawDate, setDrawDate] = useState<string>(new Date().toISOString().slice(0, 10));
  const [label, setLabel] = useState<string>('');
  const [result, setResult] = useState<TrajectoryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  // Load any user-cached series on mount (their own device, user-controlled).
  useEffect(() => {
    const local = loadLocal();
    if (local) setDraws(local.draws);
  }, []);

  function addDraw(values: BiomarkerInput) {
    const next = [...draws, { draw_date: drawDate, values, label: label.trim() || null }];
    setDraws(next);
    setLabel('');
    saveLocal({ draws: next });
  }

  async function analyze() {
    if (draws.length === 0) { setError('Add at least one dated draw.'); return; }
    setIsLoading(true); setError(null);
    try {
      const series: BiomarkerSeries = { draws };
      setResult(await submitSeries(series));
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Something went wrong.');
    } finally {
      setIsLoading(false);
    }
  }

  function onImport(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    file.text().then((text) => {
      try {
        const series = parseHealthFile(text);
        setDraws(series.draws);
        saveLocal(series);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Could not read that file.');
      }
    });
  }

  function resetAll() {
    setDraws([]); setResult(null); clearLocal();
  }

  return (
    <div style={{ maxWidth: 860, margin: '0 auto', padding: '32px 24px', display: 'flex', flexDirection: 'column', gap: 20 }}>
      <div>
        <p className="eyebrow" style={{ marginBottom: 4 }}>Longitudinal Tracking</p>
        <h1 className="display">Your Cardiometabolic Timeline</h1>
        <p className="body" style={{ marginTop: 8 }}>
          Add lab draws from different dates to see how your values move over time.
          Your data stays on your device — nothing is stored on our servers. Export
          a file to keep it; import it later to continue.
        </p>
      </div>

      {/* Draw meta */}
      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 16 }}>
          <label style={{ display: 'block' }}>
            <span style={{ display: 'block', fontSize: 13, marginBottom: 6 }}>Draw date</span>
            <input type="date" className="input" value={drawDate} max={new Date().toISOString().slice(0, 10)}
              onChange={(e) => setDrawDate(e.target.value)} />
          </label>
          <label style={{ display: 'block' }}>
            <span style={{ display: 'block', fontSize: 13, marginBottom: 6 }}>Label (optional)</span>
            <input type="text" className="input" placeholder="e.g. after starting statin"
              value={label} onChange={(e) => setLabel(e.target.value)} />
          </label>
        </div>
        <BiomarkerForm onSubmit={addDraw} submitLabel="Add this draw" />
      </div>

      {/* Draws added */}
      {draws.length > 0 && (
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          <span className="eyebrow">Draws added ({draws.length})</span>
          {draws.map((d, i) => (
            <div key={i} style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13 }}>
              <span>{d.draw_date}{d.label ? ` — ${d.label}` : ''}</span>
              <span style={{ color: 'var(--ink-soft)' }}>
                {Object.entries(d.values as unknown as Record<string, unknown>).filter(([k, v]) => v != null
                  && !['sex', 'south_asian', 'bp_med', 'chol_med', 'insulin', 'dm_pills'].includes(k)).length} values
              </span>
            </div>
          ))}
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: 8 }}>
            <button className="btn btn-primary" onClick={analyze} disabled={isLoading}>
              {isLoading ? 'Analyzing…' : 'See My Timeline'}
            </button>
            <button className="btn btn-outline" onClick={() => exportHealthFile({ draws })}>Export my file</button>
            <button className="btn btn-text" onClick={() => fileRef.current?.click()}>Import a file</button>
            <button className="btn btn-text" onClick={resetAll}>Clear all</button>
            <input ref={fileRef} type="file" accept="application/json" style={{ display: 'none' }} onChange={onImport} />
          </div>
        </div>
      )}

      {draws.length === 0 && (
        <div className="card" style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
          <span className="body">Have a saved file?</span>
          <button className="btn btn-outline" onClick={() => fileRef.current?.click()}>Import a file</button>
          <input ref={fileRef} type="file" accept="application/json" style={{ display: 'none' }} onChange={onImport} />
        </div>
      )}

      {error && (
        <div role="alert" style={{ padding: '12px 16px', borderRadius: 8, fontSize: 13,
          backgroundColor: 'var(--high-tint)', color: '#410E0B' }}>{error}</div>
      )}

      {result && (
        <>
          <Timeline trajectories={result.trajectories} interventions={result.interventions} />
          <TrajectorySummary trajectories={result.trajectories} interventions={result.interventions}
            disclaimer={result.disclaimer} />
        </>
      )}
    </div>
  );
}
