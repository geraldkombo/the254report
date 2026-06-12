import type { Alert, CountyScore, GeoJsonFeatureCollection } from "./types"

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api"

async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`)
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return (await res.json()) as T
}

async function apiPatch<T>(path: string, apiKey: string): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": apiKey,
    },
  })
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return (await res.json()) as T
}

async function apiPost<T>(path: string, apiKey: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": apiKey,
    },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return (await res.json()) as T
}

export const api = {
  baseUrl: API_BASE_URL,
  counties: () => apiGet<GeoJsonFeatureCollection>("/counties?simplify=0.01"),
  scoresLatest: () => apiGet<CountyScore[]>("/scores/latest"),
  scoresByYear: (year: number) => apiGet<CountyScore[]>(`/scores?year=${year}`),
  alerts: () => apiGet<Alert[]>("/alerts/active"),
  waterpoints: (county?: string) => apiGet<GeoJsonFeatureCollection>(county ? `/waterpoints?county=${county}` : "/waterpoints"),
  resolveAlert: (id: string, apiKey: string) => apiPatch<{ id: string; resolved_at: string }>(`/alerts/${id}/resolve`, apiKey),
  compute: (year: number | null, period: string | null, apiKey: string) =>
    apiPost<{ enqueued: boolean; year: number; period: string; task_id: string | null }>(
      "/compute/scores",
      apiKey,
      { year, period }
    ),
}
