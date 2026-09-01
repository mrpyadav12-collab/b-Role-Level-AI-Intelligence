// Thin fetch wrapper around the FastAPI backend.
// All calls go to /api/* which Vercel routes to the Python service (prefix stripped).

import type {
  AnalysisResult,
  DashboardResponse,
  Evidence,
  Methodology,
  RoleDetailResponse,
  RolesResponse,
} from "./types"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ?? ""
const BASE = API_BASE_URL ? `${API_BASE_URL}/api` : "/api"

export class ApiError extends Error {
  status: number
  constructor(message: string, status: number) {
    super(message)
    this.status = status
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response
  try {
    res = await fetch(`${BASE}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    })
  } catch {
    throw new ApiError("Could not reach the analysis service. Please try again.", 0)
  }
  if (!res.ok) {
    let detail = `Request failed (${res.status})`
    try {
      const body = await res.json()
      if (body?.detail) detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail)
    } catch {
      /* ignore parse errors */
    }
    throw new ApiError(detail, res.status)
  }
  return res.json() as Promise<T>
}

export const api = {
  dashboard: () => request<DashboardResponse>("/dashboard"),
  listRoles: (params?: { search?: string; department?: string }) => {
    const q = new URLSearchParams()
    if (params?.search) q.set("search", params.search)
    if (params?.department) q.set("department", params.department)
    const qs = q.toString()
    return request<RolesResponse>(`/roles${qs ? `?${qs}` : ""}`)
  },
  getRole: (id: number) => request<RoleDetailResponse>(`/roles/${id}`),
  analyzeRole: (id: number, force = false) =>
    request<AnalysisResult>(`/roles/${id}/analyze${force ? "?force=true" : ""}`, { method: "POST" }),
  compare: (a: number, b: number) => request<{ a: AnalysisResult; b: AnalysisResult }>(`/compare?a=${a}&b=${b}`),
  createRole: (payload: { name: string; department?: string; description?: string }) =>
    request<{ role_id: number; analysis: AnalysisResult }>("/roles", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  evidence: () => request<{ evidence: Evidence[] }>("/evidence"),
  methodology: () => request<Methodology>("/methodology"),
}
