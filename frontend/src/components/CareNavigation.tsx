'use client';
/**
 * frontend/src/components/CareNavigation.tsx
 * Informational next-step prompts (family/cascade screening, culturally-tailored
 * prevention support). Routes the patient toward people and programs — never
 * clinical advice. Renders nothing when there are no applicable prompts.
 */
import type { CareNavigationItem } from '@/lib/types';

export function CareNavigation({ items }: { items: CareNavigationItem[] }) {
  if (!items || items.length === 0) return null;

  return (
    <section className="card">
      <p className="eyebrow" style={{ marginBottom: 4 }}>Next steps</p>
      <h2 className="title" style={{ marginBottom: 16 }}>Things you might discuss</h2>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        {items.map((item) => (
          <div key={item.title} style={{
            padding: 14, borderRadius: 'var(--radius-sm)',
            border: '1px solid var(--hairline)', background: 'var(--surface)',
          }}>
            <p style={{ fontSize: 13, fontWeight: 600, color: 'var(--ink)', marginBottom: 6 }}>{item.title}</p>
            <p className="caption" style={{ lineHeight: 1.55, color: 'var(--ink-soft)' }}>{item.description}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
