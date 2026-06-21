import type { Metadata } from 'next';
import { NavBar } from '@/components/NavBar';
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
          fontSize: 12, letterSpacing: '0.01em',
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
            <svg width="26" height="26" viewBox="0 0 26 26" fill="none" aria-hidden="true">
              <rect width="26" height="26" rx="7" fill="var(--primary)" />
              <path d="M5 14.5h3l1.6-4.2 2.5 7 1.8-4.3 1.3 2.2H21" stroke="#fff"
                strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" fill="none" />
            </svg>
            <span style={{ fontWeight: 600, fontSize: 15, letterSpacing: '-0.01em', color: 'var(--ink)' }}>
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
      </body>
    </html>
  );
}
