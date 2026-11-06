import type { LucideIcon } from 'lucide-react'
import {
  Cloud,
  CloudDrizzle,
  CloudFog,
  CloudHail,
  CloudLightning,
  CloudRain,
  CloudSnow,
  CloudSun,
  Sun,
} from 'lucide-react'

// FMI "WeatherSymbol3" codes: 1–3 cloudiness, then two-digit codes where the tens give the kind of weather
// and the ones its intensity (1 light, 2 moderate, 3 heavy). https://www.ilmatieteenlaitos.fi/latauspalvelun-pikaohje
const KINDS: Record<number, [LucideIcon, string]> = {
  2: [CloudDrizzle, 'showers'],
  3: [CloudRain, 'rain'],
  4: [CloudSnow, 'snow showers'],
  5: [CloudSnow, 'snowfall'],
  6: [CloudLightning, 'thunder'],
  7: [CloudHail, 'sleet showers'],
  8: [CloudHail, 'sleet'],
}
const INTENSITY = ['', 'Light ', '', 'Heavy ']

export function describeWeather(code: number | null): { icon: LucideIcon; label: string } {
  if (code === 1) return { icon: Sun, label: 'Clear' }
  if (code === 2) return { icon: CloudSun, label: 'Partly cloudy' }
  if (code === 3) return { icon: Cloud, label: 'Cloudy' }
  if (code === 91) return { icon: CloudFog, label: 'Haze' }
  if (code === 92) return { icon: CloudFog, label: 'Fog' }

  const kind = code !== null ? KINDS[Math.floor(code / 10)] : undefined
  if (!kind || code === null) return { icon: Cloud, label: 'Forecast' }
  const [icon, name] = kind
  const label = `${INTENSITY[code % 10] ?? ''}${name}`
  return { icon, label: label.charAt(0).toUpperCase() + label.slice(1) }
}

const COMPASS = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']

/** Wind direction in degrees (where the wind blows from) -> "SW" */
export const compassDirection = (degrees: number) => COMPASS[Math.round(degrees / 45) % 8]
