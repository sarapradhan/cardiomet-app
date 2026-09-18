import type { Metadata } from 'next';
import { NavBar } from '@/components/NavBar';
import { DisplaySettings } from '@/components/DisplaySettings';
import './globals.css';

export const viewport = { width: 'device-width', initialScale: 1 };

export const metadata: Metadata = {
  title: 'CardioMet Lens — Cardiometabolic lab context',
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
          fontSize: 11.5, letterSpacing: '0.02em', fontFamily: "'DM Mono', monospace",
        }}>
          Educational tool · not a diagnosis · discuss results with your clinician
        </div>

        {/* App bar */}
        <header role="banner" className="app-bar" style={{
          background: 'rgba(255,253,250,0.85)', backdropFilter: 'saturate(180%) blur(12px)',
          borderBottom: '1px solid var(--hairline)',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          position: 'sticky', top: 0, zIndex: 20,
        }}>
          <a href="/" className="app-brand" style={{ display: 'flex', alignItems: 'center', textDecoration: 'none' }}>
            {/* Brand mark — recreated from the marketing site's .brand-mark
                (three rotated bars over a solid pine circle), not a gradient. */}
            <span aria-hidden="true" style={{
              position: 'relative', width: 28, height: 28, flex: '0 0 auto',
              borderRadius: '50% 50% 48% 52%', background: 'var(--pine)',
              overflow: 'hidden',
            }}>
              <span style={{ position: 'absolute', display: 'block', width: 3, height: 8, left: 8, top: 10, borderRadius: 5, background: 'var(--teal-light)', transform: 'rotate(38deg)' }} />
              <span style={{ position: 'absolute', display: 'block', width: 3, height: 15, left: 13, top: 7, borderRadius: 5, background: 'var(--teal-light)', transform: 'rotate(38deg)' }} />
              <span style={{ position: 'absolute', display: 'block', width: 3, height: 10, left: 18, top: 10, borderRadius: 5, background: 'var(--teal-light)', transform: 'rotate(38deg)' }} />
            </span>
            <span className="app-wordmark" style={{ fontFamily: "'Manrope', Arial, sans-serif", fontWeight: 800, letterSpacing: '-0.045em', color: 'var(--ink)' }}>
              CardioMet<span style={{ color: 'var(--teal)' }}>Lens</span>
            </span>
          </a>
          <NavBar />
        </header>

        <main id="main" role="main" style={{ minHeight: 'calc(100vh - 140px)' }}>{children}</main>

        <footer role="contentinfo" style={{ borderTop: '1px solid var(--hairline)', padding: '24px 20px', textAlign: 'center', background: 'var(--surface)' }}>
          {/* Static, site-wide chrome. This named both cohorts while a selector
              existed; the second cohort was removed on 2026-08-30 (see
              docs/SAHC_COHORT.md), so naming the one registered cohort is accurate
              again. If a second cohort is ever registered this must go back to a
              cohort-neutral phrasing — static chrome cannot know which cohort a
              given result used. Guideline thresholds are population-independent
              (see README), so those are safe to state unconditionally. */}
          <p className="caption" style={{ margin: 0 }}>
            Population benchmark: NHANES Non-Hispanic Asian · Classification
            thresholds: ACC/AHA · ADA · NCEP · WHO
          </p>
          <p className="caption" style={{ marginTop: 4 }}>Educational tool · not a medical device</p>
        </footer>

        <DisplaySettings />
      </body>
    </html>
  );
}
