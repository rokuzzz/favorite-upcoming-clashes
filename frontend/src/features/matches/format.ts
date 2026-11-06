// Games are shown in Finnish local time, whatever the viewer's own time zone is.
const matchTimeFormat = new Intl.DateTimeFormat('en-GB', {
  timeZone: 'Europe/Helsinki',
  weekday: 'short',
  day: 'numeric',
  month: 'short',
  hour: '2-digit',
  minute: '2-digit',
})

/** "2026-11-11T16:30:00Z" -> "Wed 11 Nov, 18:30" */
export const formatMatchTime = (isoUtc: string) => matchTimeFormat.format(new Date(isoUtc))
