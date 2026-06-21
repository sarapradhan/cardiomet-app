'use client';
/**
 * frontend/src/components/MedicationNotes.tsx
 * Surfaces medication notes from the API. These do not change any classification;
 * they remind the reader that a value may reflect treatment.
 */
interface Props {
  notes: string[];
}

export function MedicationNotes({ notes }: Props) {
  if (notes.length === 0) return null;
  return (
    <section className="panel-sunken" style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      <span className="eyebrow">Medication Notes</span>
      {notes.map((note, i) => (
        <p key={i} style={{ fontSize: 13, lineHeight: 1.5, margin: 0, color: 'var(--ink-soft)' }}>
          {note}
        </p>
      ))}
    </section>
  );
}
