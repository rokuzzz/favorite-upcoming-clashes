import { CloudOff, Droplets, Wind } from 'lucide-react'

import type { WeatherForecast } from '@/api/types'
import { compassDirection, describeWeather } from './symbols'

// Presentational: the forecast at the arena for the hour the match starts.
export function WeatherInfo({ weather }: { weather: WeatherForecast }) {
  if (!weather.available) {
    return (
      <p className="flex items-center gap-2">
        <CloudOff className="size-4" />
        {weather.message}
      </p>
    )
  }

  const { icon: Icon, label } = describeWeather(weather.weatherSymbol)
  return (
    <p className="flex flex-wrap items-center gap-x-4 gap-y-1">
      <span className="flex items-center gap-2 font-medium text-foreground">
        <Icon className="size-4" />
        {weather.temperatureC !== null && `${Math.round(weather.temperatureC) || 0} °C`} {label}
      </span>
      {weather.windSpeedMs !== null && (
        <span className="flex items-center gap-1" title="Wind">
          <Wind className="size-4" />
          {weather.windSpeedMs.toFixed(1)} m/s
          {weather.windDirectionDeg !== null && ` ${compassDirection(weather.windDirectionDeg)}`}
        </span>
      )}
      {weather.precipitationMm !== null && (
        <span className="flex items-center gap-1" title="Precipitation">
          <Droplets className="size-4" />
          {weather.precipitationMm.toFixed(1)} mm/h
        </span>
      )}
    </p>
  )
}
