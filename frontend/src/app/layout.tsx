import type { Metadata } from 'next';
import Link from 'next/link';
import './globals.css';

export const metadata: Metadata = {
  title: 'SAHC RiskLens',
  description: 'Responsible cardiometabolic benchmarking for South Asian heart health. Educational use only.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        {/* Global disclaimer — structural, always visible, cannot be removed per page */}
        <div style={{
          backgroundColor: '#FFF8E1',
          borderBottom: '1px solid #FFE082',
          color: '#E65100',
          padding: '8px 16px',
          textAlign: 'center',
          fontSize: '12px',
          fontWeight: 500,
          letterSpacing: '0.01em',
        }}>
          Educational tool only · Does not diagnose or prescribe · Discuss results with your clinician
        </div>

        {/* Top app bar — Material Design */}
        <header style={{
          backgroundColor: 'var(--md-surface)',
          boxShadow: 'var(--md-elevation-1)',
          padding: '14px 24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          position: 'sticky',
          top: 0,
          zIndex: 10,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              width: 32, height: 32, borderRadius: 8,
              backgroundColor: 'var(--md-primary)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              color: '#fff', fontSize: 14, fontWeight: 600,
            }}>R</div>
            <span style={{ fontWeight: 600, fontSize: 15, letterSpacing: '-0.01em',
              color: 'var(--md-on-surface)' }}>
              SAHC RiskLens
            </span>
          </div>
          <nav style={{ display: 'flex', gap: 4 }}>
            {([['/', 'Home'], ['/benchmark', 'Benchmark']] as [string,string][]).map(([href, label]) => (
              <Link key={href} href={href} className="md-nav-link">
                {label}
              </Link>
            ))}
          </nav>
        </header>

        <main style={{ backgroundColor: 'var(--md-background)', minHeight: '100vh' }}>
          {children}
        </main>

        <footer style={{
          backgroundColor: 'var(--md-surface)',
          borderTop: '1px solid var(--md-outline-variant)',
          padding: '28px 24px',
          textAlign: 'center',
        }}>
          <p style={{ fontSize: 11, color: 'var(--md-on-surface-variant)', margin: 0 }}>
            Reference: NHANES Non-Hispanic Asian · 2017–2018 · RIDRETH3 = 6
          </p>
          <p style={{ fontSize: 11, color: 'var(--md-on-surface-variant)', marginTop: 4 }}>
            Thresholds: ACC/AHA 2018 · ADA 2024 · WHO · Not a medical device
          </p>
        </footer>
      </body>
    </html>
  );
}
