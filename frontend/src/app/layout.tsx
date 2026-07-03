import type { Metadata } from 'next';
import { NavBar } from '@/components/NavBar';
import { DisplaySettings } from '@/components/DisplaySettings';
import './globals.css';

export const viewport = { width: 'device-width', initialScale: 1 };

export const metadata: Metadata = {
  title: 'SAHC RiskLens — Cardiometabolic lab context',
  description: 'Understand your cardiometabolic labs against clinical guidelines and a population benchmark. Educational use only — not a diagnosis.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <a href="#main" className="skip-link">Skip to content</a>
        {/* Structural disclaimer — always present */}
        <div style={{
          background: 'var(--surface)', borderBottom: '1px solid var(--hairline)',
          color: 'var(--ink-soft)', padding: '7px 20px', textAlign: 'center',
          fontSize: 11.5, letterSpacing: '0.02em', fontFamily: "'Space Mono', ui-monospace, monospace",
        }}>
          Educational tool · not a diagnosis · discuss results with your clinician
        </div>

        {/* App bar */}
        <header role="banner" style={{
          background: 'rgba(255,255,255,0.82)', backdropFilter: 'saturate(180%) blur(12px)',
          borderBottom: '1px solid var(--hairline)', padding: '12px 20px',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          position: 'sticky', top: 0, zIndex: 20,
        }}>
          <a href="/" style={{ display: 'flex', alignItems: 'center', gap: 11, textDecoration: 'none' }}>
            <span aria-hidden="true" style={{
              width: 30, height: 30, borderRadius: 10,
              background: 'linear-gradient(145deg, #16A5B5, #0E7C90)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              boxShadow: '0 4px 11px -5px rgba(14,124,144,0.7)',
            }}>
              <span style={{ width: 12, height: 12, borderRadius: 999, border: '2.5px solid rgba(255,255,255,0.94)' }} />
            </span>
            <span style={{ fontFamily: "'Space Grotesk', system-ui, sans-serif", fontWeight: 600, fontSize: 16, letterSpacing: '-0.02em', color: 'var(--ink)' }}>
              SAHC RiskLens
            </span>
          </a>
          <NavBar />
        </header>

        <main id="main" role="main" style={{ minHeight: 'calc(100vh - 140px)' }}>{children}</main>

        <footer role="contentinfo" style={{ borderTop: '1px solid var(--hairline)', padding: '24px 20px', textAlign: 'center', background: 'var(--surface)' }}>
          <p className="caption" style={{ margin: 0 }}>
            Reference: NHANES Non-Hispanic Asian (2017–2018) · Thresholds: ACC/AHA · ADA · NCEP · WHO
          </p>
          <p className="caption" style={{ marginTop: 4 }}>Educational tool · not a medical device</p>
        </footer>

        <DisplaySettings />
      </body>
    </html>
  );
}
