/**
 * frontend/src/lib/api.ts — API client.
 * Never hardcode API URL — use NEXT_PUBLIC_API_URL only.
 */
import type { BiomarkerInput, BenchmarkResponse, ThresholdsResponse } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

export async function submitBiomarkers(input: BiomarkerInput): Promise<BenchmarkResponse> {
  const res = await fetch(`${API_BASE}/api/v1/benchmark`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error((err as { detail?: string }).detail ?? `API error: ${res.status}`);
  }
  return res.json() as Promise<BenchmarkResponse>;
}

export async function getThresholds(): Promise<ThresholdsResponse> {
  const res = await fetch(`${API_BASE}/api/v1/thresholds`);
  if (!res.ok) throw new Error(`Thresholds API error: ${res.status}`);
  return res.json() as Promise<ThresholdsResponse>;
}

export async function healthCheck(): Promise<{ status: string; nhanes_loaded: boolean; mode: string }> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Health check failed');
  return res.json();
}

export async function submitSeries(series: import('./types').BiomarkerSeries):
    Promise<import('./types').TrajectoryResponse> {
  const res = await fetch(`${API_BASE}/api/v1/trajectory`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(series),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error((err as { detail?: string }).detail ?? `API error: ${res.status}`);
  }
  return res.json() as Promise<import('./types').TrajectoryResponse>;
}
