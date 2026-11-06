// Short names for the API types generated from the backend's OpenAPI schema.
// Regenerate schema.ts with `npm run gen:api` whenever backend models change.
import type { components } from './schema'

type Schemas = components['schemas']

export type Team = Schemas['Team']
export type Venue = Schemas['Venue']
export type UpcomingMatch = Schemas['UpcomingMatch']
export type MatchesResponse = Schemas['MatchesResponse']
