'use client';
/**
 * frontend/src/components/TrajectorySummary.tsx
 * Plain-language, per-biomarker summary of movement over time, plus intervention
 * notes. All language is descriptive and comes from / mirrors the API. Always
 * renders the disclaimer and a "few draws can mislead" limitation.
 */
import type { BiomarkerTrajectory, InterventionMarker } from '@/lib/types';
import { chipClass } from '@/lib/categoryStyles';

interface Props {
  trajectories: BiomarkerTrajectory[];
  interventions: InterventionMarker[];
  disclaimer: string;
}

const DIRECTION_LABEL: Record<string, string> = {
  improving: 'moving toward the typical range',
  worsening: 'moving away from the typical range',
  stable: 'about the same',
  insufficient_data: 'not enough dated values yet',
};

export function TrajectorySummary({ trajectories, interventions, disclaimer }: Props) {
  const moved = trajectories.filter((t) => t.direction === 'improving' || t.direction === 'worsening');

  return (
    <section className="card" style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
      <p className="eyebrow" style={{ marginBottom: 4 }}>Summary</p>
      <h2 className="title" style={{ marginBottom: 12 }}>What Changed</h2>

      {moved.length === 0 ? (
        <p className="body">No clear movement across your draws yet. Add more dated
          values over time to see trends.</p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {moved.map((t) => (
            <div key={t.biomarker} style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                <span style={{ fontSize: 13, fontWeight: 600 }}>{t.biomarker}</span>
                <span style={{ fontSize: 13, color: 'var(--ink-soft)' }}>
                  {DIRECTION_LABEL[t.direction]}
                  {t.change_absolute !== null ? ` (${t.change_absolute > 0 ? '+' : ''}${t.change_absolute} ${t.unit})` : ''}
                </span>
              </div>
              {t.transitions.map((tr, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12 }}>
                  <span className={chipClass(tr.from_category)}>{tr.from_category}</span>
                  <span style={{ color: 'var(--ink-soft)' }}>→</span>
                  <span className={chipClass(tr.to_category)}>{tr.to_category}</span>
                </div>
              ))}
            </div>
          ))}
        </div>
      )}

      {interventions.length > 0 && (
        <div style={{ marginTop: 12, display: 'flex', flexDirection: 'column', gap: 8 }}>
          <span className="eyebrow">Around a medication change</span>
          {interventions.map((iv, i) => (
            <div key={i} className="panel-sunken" style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
              <span style={{ fontSize: 13, fontWeight: 500 }}>{iv.change} ({iv.draw_date})</span>
              {iv.observed_effects.map((e, j) => (
                <span key={j} style={{ fontSize: 12, color: 'var(--ink-soft)' }}>{e}</span>
              ))}
            </div>
          ))}
        </div>
      )}

      {/* Disclaimer (from API) + trajectory-specific limitation, always shown */}
      <div style={{ marginTop: 16, padding: '12px 16px', borderRadius: 8, fontSize: 12,
        backgroundColor: '#FFF8E1', color: '#E65100', border: '1px solid #FFE082' }}>
        {disclaimer}
      </div>
      <p style={{ fontSize: 11, color: 'var(--ink-soft)', marginTop: 8 }}>
        A small number of draws can be misleading. Lab values vary for many reasons,
        and these trends are context for a conversation with your clinician — not conclusions.
      </p>
    </section>
  );
}
