'use client';
/**
 * frontend/src/components/GuidedTour.tsx
 * A lightweight, dependency-free guided tour. Highlights elements marked with
 * data-tour="..." and shows a positioned tooltip with prev/next/skip. Used to
 * make the app self-guiding for demos and first-time visitors. Remembers
 * completion in localStorage so it doesn't nag returning users.
 */
import { useEffect, useLayoutEffect, useState, useCallback } from 'react';

export interface TourStep {
  anchor: string;          // data-tour value to spotlight (or '' for centered)
  title: string;
  body: string;
}

const SEEN_KEY = 'sahc_tour_seen_v1';

export function GuidedTour({ steps, tourId = 'default', autoStart = false }:
  { steps: TourStep[]; tourId?: string; autoStart?: boolean }) {
  const [active, setActive] = useState(false);
  const [i, setI] = useState(0);
  const [rect, setRect] = useState<DOMRect | null>(null);

  // Auto-start once per visitor (unless they've seen it).
  useEffect(() => {
    if (!autoStart) return;
    let seen = false;
    try { seen = localStorage.getItem(`${SEEN_KEY}:${tourId}`) === '1'; } catch { /* ignore */ }
    if (!seen) setActive(true);
  }, [autoStart, tourId]);

  // Listen for a manual "start tour" event (button can dispatch it).
  useEffect(() => {
    const start = () => { setI(0); setActive(true); };
    window.addEventListener('sahc:start-tour', start);
    return () => window.removeEventListener('sahc:start-tour', start);
  }, []);

  const measure = useCallback(() => {
    const step = steps[i];
    if (!step || !step.anchor) { setRect(null); return; }
    const el = document.querySelector(`[data-tour="${step.anchor}"]`);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      setRect(el.getBoundingClientRect());
    } else {
      setRect(null);
    }
  }, [i, steps]);

  useLayoutEffect(() => {
    if (!active) return;
    measure();
    const onResize = () => measure();
    window.addEventListener('resize', onResize);
    window.addEventListener('scroll', onResize, true);
    return () => {
      window.removeEventListener('resize', onResize);
      window.removeEventListener('scroll', onResize, true);
    };
  }, [active, measure]);

  if (!active) return null;
  const step = steps[i];
  const last = i === steps.length - 1;

  function finish() {
    setActive(false);
    try { localStorage.setItem(`${SEEN_KEY}:${tourId}`, '1'); } catch { /* ignore */ }
  }

  // Tooltip position: below the anchor if known, else centered.
  const pad = 8;
  const tipTop = rect ? Math.min(rect.bottom + pad, window.innerHeight - 220) : window.innerHeight / 2 - 110;
  const tipLeft = rect
    ? Math.max(16, Math.min(rect.left, window.innerWidth - 340))
    : window.innerWidth / 2 - 170;

  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 1000 }} role="dialog" aria-modal="true"
      aria-label="Guided tour">
      {/* Dim overlay; clicking it skips */}
      <div onClick={finish} style={{ position: 'absolute', inset: 0, background: 'rgba(24,34,47,0.45)' }} />

      {/* Spotlight ring around the anchor */}
      {rect && (
        <div style={{
          position: 'absolute', top: rect.top - 6, left: rect.left - 6,
          width: rect.width + 12, height: rect.height + 12, borderRadius: 12,
          boxShadow: '0 0 0 3px var(--primary), 0 0 0 9999px rgba(24,34,47,0.45)',
          pointerEvents: 'none', transition: 'all .2s ease',
        }} />
      )}

      {/* Tooltip card */}
      <div style={{
        position: 'absolute', top: tipTop, left: tipLeft, width: 320,
        background: 'var(--surface)', borderRadius: 14, padding: 18,
        boxShadow: 'var(--shadow-2)', border: '1px solid var(--hairline)',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 6 }}>
          <span className="eyebrow">{`Step ${i + 1} of ${steps.length}`}</span>
          <button onClick={finish} className="btn btn-text" style={{ height: 24, fontSize: 12 }}>Skip</button>
        </div>
        <h3 className="title" style={{ fontSize: 16, marginBottom: 6 }}>{step.title}</h3>
        <p className="body" style={{ fontSize: 13.5, marginBottom: 14 }}>{step.body}</p>
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8 }}>
          <button className="btn btn-text" style={{ height: 36 }}
            onClick={() => setI((n) => Math.max(0, n - 1))} disabled={i === 0}>Back</button>
          {last ? (
            <button className="btn btn-primary" style={{ height: 36 }} onClick={finish}>Done</button>
          ) : (
            <button className="btn btn-primary" style={{ height: 36 }} onClick={() => setI((n) => n + 1)}>Next</button>
          )}
        </div>
      </div>
    </div>
  );
}

/** A small button that (re)starts the tour from anywhere. */
export function TourButton({ label = 'Take a tour' }: { label?: string }) {
  return (
    <button className="btn btn-outline" style={{ height: 34, fontSize: 13 }}
      onClick={() => window.dispatchEvent(new Event('sahc:start-tour'))}>
      {label}
    </button>
  );
}
