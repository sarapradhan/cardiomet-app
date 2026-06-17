import Link from 'next/link';

const pillStyle = {
  display: 'inline-flex', alignItems: 'center',
  padding: '4px 12px', borderRadius: 20, fontSize: 11, fontWeight: 500,
  backgroundColor: 'var(--md-surface-variant)',
  color: 'var(--md-on-surface-variant)',
};

export default function HomePage() {
  return (
    <div style={{ maxWidth: 560, margin: '0 auto', padding: '72px 24px', textAlign: 'center' }}>

      {/* Phase badge */}
      <div style={{ marginBottom: 24 }}>
        <span style={{ ...pillStyle,
          backgroundColor: 'var(--md-primary-container)',
          color: 'var(--md-on-primary-container)' }}>
          Phase 1 · Demo
        </span>
      </div>

      {/* Headline */}
      <h1 style={{ fontSize: 40, fontWeight: 300, letterSpacing: '-0.02em',
        color: 'var(--md-on-surface)', margin: '0 0 12px' }}>
        SAHC RiskLens
      </h1>
      <p style={{ fontSize: 18, fontWeight: 300, color: 'var(--md-on-surface-variant)',
        margin: '0 0 8px', lineHeight: 1.5 }}>
        Cardiometabolic benchmarking for South Asian heart health
      </p>
      <p style={{ fontSize: 13, color: 'var(--md-on-surface-variant)', margin: '0 0 48px' }}>
        Clinical context · NHANES reference · Physician discussion support
      </p>

      {/* CTA card */}
      <div className="md-card" style={{ marginBottom: 32 }}>
        <p style={{ fontSize: 14, color: 'var(--md-on-surface-variant)',
          marginBottom: 24, lineHeight: 1.6 }}>
          Enter your biomarkers to see clinical threshold context and
          NHANES Non-Hispanic Asian reference benchmarks.
        </p>
        <Link href="/benchmark" className="md-btn-primary">
          Start Benchmark
        </Link>
      </div>

      {/* Info pills */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, justifyContent: 'center' }}>
        {['For physician discussion — not diagnosis', 'No data stored', 'Guideline-sourced'].map(t => (
          <span key={t} style={pillStyle}>{t}</span>
        ))}
      </div>
    </div>
  );
}
