'use client';
/**
 * frontend/src/components/Legend.tsx
 * The color-coding legend — the app's signature, learnable visual language.
 * Two rows: clinical status (in range / elevated / high / not provided) and
 * biomarker groups (lipids / glucose / blood pressure / body).
 */
import { GROUP_ORDER, GROUP_LABEL } from '@/lib/biomarkerMeta';

const STATUS = [
  { tone: 'normal', label: 'In range' },
  { tone: 'elevated', label: 'Elevated' },
  { tone: 'high', label: 'High' },
  { tone: 'missing', label: 'Not provided' },
];

export function Legend({ compact = false }: { compact?: boolean }) {
  return (
    <div className="panel-sunken" style={{ display: 'flex', flexWrap: 'wrap', gap: compact ? 16 : 24, alignItems: 'center' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
        <span className="caption" style={{ fontWeight: 600 }}>Status</span>
        {STATUS.map((s) => (
          <span key={s.tone} className={`chip chip-${s.tone}`}>
            <span className="chip-dot" />{s.label}
          </span>
        ))}
      </div>
      {!compact && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
          <span className="caption" style={{ fontWeight: 600 }}>Panels</span>
          {GROUP_ORDER.map((g) => (
            <span key={g} style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
              <span style={{ width: 10, height: 10, borderRadius: 3, background: `var(--grp-${g})` }} />
              <span className="caption">{GROUP_LABEL[g]}</span>
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
