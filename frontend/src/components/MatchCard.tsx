import { Clock, MapPin } from 'lucide-react'

import type { UpcomingMatch } from '@/api/types'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { formatMatchTime } from '@/lib/format'

// Presentational only: everything it shows comes in through props.
export function MatchCard({ match }: { match: UpcomingMatch }) {
  const { opponent, venue } = match

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-3">
          {opponent.logoUrl && <img src={opponent.logoUrl} alt="" className="size-10 object-contain" />}
          <CardTitle className="flex-1 text-lg">
            {match.isHome ? 'vs' : '@'} {opponent.name}
          </CardTitle>
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
      </CardContent>
    </Card>
  )
}
