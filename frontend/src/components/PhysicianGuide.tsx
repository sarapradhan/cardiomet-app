'use client';
/**
 * frontend/src/components/PhysicianGuide.tsx
 * Renders the template-based physician discussion guide. Each item is a prompt
 * the reader can raise with their clinician — never an instruction or diagnosis.
 * All text is produced server-side by a fixed template (no LLM).
 */
import type { PhysicianGuideItem } from '@/lib/types';
import { chipClass } from '@/lib/categoryStyles';

interface Props {
  items: PhysicianGuideItem[];
}

export function PhysicianGuide({ items }: Props) {
  return (
    <section className="card" style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
      <p className="eyebrow" style={{ marginBottom: 4 }}>For Your Appointment</p>
      <h2 className="title" style={{ marginBottom: 4 }}>Questions to Discuss With Your Clinician</h2>
      {items.length === 0 ? (
        <p className="body" style={{ marginTop: 12 }}>
          None of your provided values fell outside the typical range. Bring any
          personal health concerns to your clinician regardless.
        </p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginTop: 12 }}>
          {items.map((item, i) => (
            <div key={i} className="panel-sunken"
              style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{ fontSize: 13, fontWeight: 600 }}>{item.biomarker}</span>
                <span className={chipClass(item.category)}>{item.category}</span>
              </div>
              <p style={{ fontSize: 13, lineHeight: 1.6, margin: 0, color: 'var(--ink-soft)' }}>
                {item.discussion_prompt}
              </p>
              <span style={{ fontSize: 10, color: 'var(--ink-faint)' }}>{item.guideline_note}</span>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
