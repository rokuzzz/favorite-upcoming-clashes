// The only module that talks to the backend. In development Vite proxies /api to FastAPI.
import type { Horizon, MatchesResponse, Team } from './types'

export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

async function request<T>(path: string): Promise<T> {
  const response = await fetch(`/api${path}`)
  if (!response.ok) {
    // FastAPI puts the error message into `detail`
    const body = await response.json().catch(() => null)
    const detail = typeof body?.detail === 'string' ? body.detail : `Request failed (${response.status})`
    throw new ApiError(response.status, detail)
  }
  return response.json() as Promise<T>
}

export const api = {
  getTeams: () => request<Team[]>('/teams'),
  getMatches: (teamId: string, days: Horizon) =>
    request<MatchesResponse>(`/matches?${new URLSearchParams({ team: teamId, days: String(days) })}`),
}
