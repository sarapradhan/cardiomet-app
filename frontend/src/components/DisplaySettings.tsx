'use client';
/**
 * frontend/src/components/DisplaySettings.tsx
 * Floating "Display" control: lets a reader widen the page on a large screen
 * instead of leaving the desktop viewport mostly empty (mobile web is the
 * primary target, so the default stays narrow). The choice is applied as the
 * --content-w CSS variable every page reads for its max-width, and persists
 * across visits via localStorage.
 */
import { useEffect, useRef, useState } from 'react';

const STORAGE_KEY = 'sahc-content-width';
const MIN = 720;
const MAX = 1440;
const STEP = 20;
const DEFAULT_WIDTH = 880;

export function DisplaySettings() {
  const [open, setOpen] = useState(false);
  const [width, setWidth] = useState(DEFAULT_WIDTH);
  const rootRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const stored = parseInt(localStorage.getItem(STORAGE_KEY) ?? '', 10);
    const initial = Number.isFinite(stored) && stored >= MIN && stored <= MAX ? stored : DEFAULT_WIDTH;
    setWidth(initial);
    document.documentElement.style.setProperty('--content-w', `${initial}px`);
  }, []);

  useEffect(() => {
    if (!open) return;
    function onKeyDown(e: KeyboardEvent) {
      if (e.key === 'Escape') setOpen(false);
    }
    function onPointerDown(e: MouseEvent) {
      if (rootRef.current && !rootRef.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener('keydown', onKeyDown);
    document.addEventListener('mousedown', onPointerDown);
    return () => {
      document.removeEventListener('keydown', onKeyDown);
      document.removeEventListener('mousedown', onPointerDown);
    };
  }, [open]);

  function handleChange(next: number) {
    setWidth(next);
    document.documentElement.style.setProperty('--content-w', `${next}px`);
    localStorage.setItem(STORAGE_KEY, String(next));
  }

  return (
    <div ref={rootRef} style={{ position: 'fixed', right: 20, bottom: 20, zIndex: 50 }}>
      {open && (
        <div
          role="dialog"
          aria-label="Display settings"
          style={{
            width: 260, background: 'var(--surface)', border: '1px solid var(--hairline)',
            borderRadius: 'var(--radius)', boxShadow: 'var(--shadow-2)', padding: 18,
            position: 'absolute', right: 0, bottom: 56,
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
            <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--ink)' }}>Display</span>
            <button
              aria-label="Close display settings"
              onClick={() => setOpen(false)}
              style={{ border: 'none', background: 'none', cursor: 'pointer', color: 'var(--ink-soft)', fontSize: 18, lineHeight: 1, padding: 0 }}
            >
              ×
            </button>
          </div>

          <label htmlFor="content-width-slider" style={{ display: 'block', fontSize: 12, fontWeight: 500, color: 'var(--ink-soft)', marginBottom: 8 }}>
            Content width
            <span className="num" style={{ float: 'right', color: 'var(--ink)' }}>{width}px</span>
          </label>
          <input
            id="content-width-slider"
            type="range"
            min={MIN}
            max={MAX}
            step={STEP}
            value={width}
            onChange={(e) => handleChange(parseInt(e.target.value, 10))}
            style={{ width: '100%', accentColor: 'var(--primary)', cursor: 'pointer' }}
          />
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10.5, color: 'var(--ink-soft)', marginTop: 4 }}>
            <span>Narrow</span>
            <span>Wide</span>
          </div>
        </div>
      )}

      <button
        aria-label="Display settings"
        aria-expanded={open}
        onClick={() => setOpen((o) => !o)}
        style={{
          width: 44, height: 44, borderRadius: 999, border: '1px solid var(--hairline)',
          background: 'var(--surface)', boxShadow: 'var(--shadow-2)', cursor: 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--primary)',
        }}
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
          <path d="M4 21v-7M4 10V3M12 21v-9M12 8V3M20 21v-5M20 12V3M1 14h6M9 8h6M17 16h6" />
        </svg>
      </button>
    </div>
  );
}
