import Link from 'next/link';
import { Legend } from '@/components/Legend';

export default function Home() {
  return (
    <div style={{ maxWidth: 880, margin: '0 auto', padding: '56px 24px 40px' }}>
      {/* Hero */}
      <p className="eyebrow" style={{ marginBottom: 14 }}>South Asian cardiometabolic health</p>
      <h1 className="display" style={{ fontSize: 'clamp(32px, 5vw, 46px)', maxWidth: 640, marginBottom: 18 }}>
        Understand your lab numbers before you see your doctor.
      </h1>
      <p className="body" style={{ fontSize: 16, maxWidth: 560, marginBottom: 28 }}>
        Enter your cardiometabolic labs to see each value against clinical guidelines
        and a population benchmark — with the South Asian risk context generic tools
        leave out. Nothing is stored; this is context for a conversation, not a diagnosis.
      </p>
      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 44 }}>
        <Link href="/benchmark" className="btn btn-primary">Check my labs</Link>
        <Link href="/timeline" className="btn btn-outline">Track over time</Link>
      </div>

      <Legend />

      {/* What you get */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16, marginTop: 32 }}>
        {[
          ['Guideline context', 'Each value placed in its category — Optimal to High — with the source guideline named (ACC/AHA, ADA, NCEP, WHO).'],
          ['Population benchmark', 'See where you sit in the NHANES Non-Hispanic Asian distribution, labeled honestly — not a false South Asian–specific claim.'],
          ['South Asian context', 'Ancestry shown as a guideline-recognized risk-enhancing factor, with lower BMI action points — as discussion context.'],
          ['Questions to ask', 'A short, plain-language list to bring to your clinician. No predictions, no treatment advice.'],
        ].map(([h, b]) => (
          <div key={h} className="card" style={{ padding: 20 }}>
            <h3 className="title" style={{ fontSize: 15, marginBottom: 6 }}>{h}</h3>
            <p className="caption" style={{ lineHeight: 1.6 }}>{b}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
