// Short names for the API types generated from the backend's OpenAPI schema.
// Regenerate schema.ts with `npm run gen:api` whenever backend models change.
import type { components } from './schema'

type Schemas = components['schemas']

export type Team = Schemas['Team']
export type Venue = Schemas['Venue']
export type UpcomingMatch = Schemas['UpcomingMatch']
export type MatchesResponse = Schemas['MatchesResponse']
// Used both as request body and response; the response variant (all fields present) is also a valid request.
export type Preferences = Schemas['Preferences-Output']

// Allowed values of `days` (backend: config.ALLOWED_HORIZONS). The schema only knows it is an integer.
export const HORIZONS = [7, 14, 21] as const
export type Horizon = (typeof HORIZONS)[number]
