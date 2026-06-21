'use client';
/**
 * frontend/src/components/LimitationsPanel.tsx
 * Always-visible limitations. This panel is structural and must never be hidden
 * or collapsed — it states what the tool is not and the key NHANES data caveat.
 * Content mirrors docs/SAFETY_AND_LIMITATIONS.md.
 */
const LIMITATIONS: string[] = [
  'This tool is educational and does not diagnose, treat, or replace clinical judgment.',
  'NHANES groups South, East, and Southeast Asians together as "Non-Hispanic Asian"; this is not a South Asian–specific cohort.',
  'South Asian risk context and BMI thresholds are guideline-based discussion points, not an empirical benchmark.',
  'Fasting glucose comes from a morning subsample; missing values are expected and are flagged, never imputed.',
  'Values measured while on medication may not reflect an untreated baseline.',
];

export function LimitationsPanel() {
  return (
    <section style={{
      background: 'var(--surface)', border: '1px solid var(--hairline)',
      borderRadius: 12, padding: 24, display: 'flex', flexDirection: 'column', gap: 12,
    }}>
      <span className="eyebrow">Important Limitations</span>
      <ul style={{ margin: 0, paddingLeft: 18, display: 'flex', flexDirection: 'column', gap: 8 }}>
        {LIMITATIONS.map((text, i) => (
          <li key={i} style={{ fontSize: 12, lineHeight: 1.6, color: 'var(--ink-soft)' }}>
            {text}
          </li>
        ))}
      </ul>
    </section>
  );
}
