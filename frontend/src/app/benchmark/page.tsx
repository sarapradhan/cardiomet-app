'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import type { BiomarkerInput, BenchmarkResponse } from '@/lib/types';
import { submitBiomarkers } from '@/lib/api';
import { BiomarkerForm } from '@/components/BiomarkerForm';

export default function BenchmarkPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(input: BiomarkerInput) {
    setIsLoading(true);
    setError(null);
    try {
      const result: BenchmarkResponse = await submitBiomarkers(input);
      // sessionStorage: cleared on tab close — never persists
      sessionStorage.setItem('benchmarkResult', JSON.stringify(result));
      router.push('/results');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 720, margin: '0 auto', padding: '32px 24px' }}>
      <div style={{ marginBottom: 32 }}>
        <p className="md-label" style={{ marginBottom: 4 }}>Biomarker Input</p>
        <h1 className="md-headline">Enter Your Lab Values</h1>
        <p className="md-body" style={{ marginTop: 8 }}>
          Every field is optional — anything you leave blank is simply flagged as
          not provided. No data is stored beyond this browser session.
        </p>
      </div>

      <BiomarkerForm onSubmit={handleSubmit} isLoading={isLoading} />

      {error && (
        <div role="alert" style={{
          marginTop: 16, padding: '12px 16px', borderRadius: 8,
          backgroundColor: 'var(--md-error-container)', color: '#410E0B', fontSize: 13,
        }}>
          {error}
        </div>
      )}
    </div>
  );
}
