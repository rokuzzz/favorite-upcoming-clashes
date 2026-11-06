import { Clock, MapPin } from 'lucide-react'

import type { UpcomingMatch } from '@/api/types'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { WeatherInfo } from '@/features/weather/WeatherInfo'
import { formatMatchTime } from './format'

// Presentational only: everything it shows comes in through props.
export function MatchCard({ match }: { match: UpcomingMatch }) {
  const { opponent, venue } = match

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-3">
          {opponent.logoUrl && <img src={opponent.logoUrl} alt="" className="size-10 object-contain" />}
          {/* Home or away is shown by the badge */}
          <CardTitle className="flex-1 text-lg">vs {opponent.name}</CardTitle>
          <Badge variant={match.isHome ? 'default' : 'secondary'}>{match.isHome ? 'Home' : 'Away'}</Badge>
        </div>
      </CardHeader>
      <CardContent className="flex flex-col gap-1 text-sm text-muted-foreground">
        <p className="flex items-center gap-2">
          <Clock className="size-4" />
          <time dateTime={match.startUtc}>{formatMatchTime(match.startUtc)}</time>
        </p>
        <p className="flex items-center gap-2">
          <MapPin className="size-4" />
          {venue.name}, {venue.city}
        </p>
        {match.weather && <WeatherInfo weather={match.weather} />}
      </CardContent>
    </Card>
  )
}

// Placeholder with the same layout as MatchCard: logo, title, badge, then time, venue and weather lines.
export function MatchCardSkeleton() {
  return (
    <Card aria-hidden>
      <CardHeader>
        <div className="flex items-center gap-3">
          <Skeleton className="size-10 rounded-full" />
          <Skeleton className="h-6 max-w-40 flex-1" />
          <Skeleton className="h-5 w-12 rounded-full" />
        </div>
      </CardHeader>
      <CardContent className="flex flex-col gap-2">
        <Skeleton className="h-4 w-36" />
        <Skeleton className="h-4 w-60" />
        <Skeleton className="h-4 w-52" />
      </CardContent>
    </Card>
  )
}
