'use client'

export interface MonedaConfig {
  codigo: string
  simbolo: string
  decimales: number
  separador_miles: string
  separador_decimal: string
  locale: string
}

let _monedaConfig: MonedaConfig = {
  codigo: 'CLP',
  simbolo: '$',
  decimales: 0,
  separador_miles: '.',
  separador_decimal: ',',
  locale: 'es-CL',
}

let _redondeoMultiplo = 10

export function setFormatConfig(config: {
  moneda?: Partial<MonedaConfig>
  redondeoMultiplo?: number
}) {
  if (config.moneda) _monedaConfig = { ..._monedaConfig, ...config.moneda }
  if (config.redondeoMultiplo !== undefined) _redondeoMultiplo = config.redondeoMultiplo
}

export function getMonedaConfig() {
  return _monedaConfig
}

export function getRedondeoMultiplo() {
  return _redondeoMultiplo
}

export function formatMoney(amount: number | string | null | undefined): string {
  const val = typeof amount === 'string' ? parseFloat(amount) : (amount || 0)
  const cfg = _monedaConfig
  const dec = typeof cfg.decimales === 'number' && !isNaN(cfg.decimales) ? cfg.decimales : 0

  try {
    const formatted = new Intl.NumberFormat(cfg.locale || 'es-CL', {
      style: 'decimal',
      minimumFractionDigits: dec,
      maximumFractionDigits: dec,
    }).format(val)

    const sepMiles = cfg.separador_miles || '.'
    const sepDec = cfg.separador_decimal || ','

    if (sepMiles !== getDefaultThousandsSeparator(cfg.locale || 'es-CL')) {
      const parts = formatted.split(getDefaultDecimalSeparator(cfg.locale || 'es-CL') || '.')
      parts[0] = parts[0].replace(new RegExp('\\' + getDefaultThousandsSeparator(cfg.locale || 'es-CL'), 'g'), sepMiles)
      return (cfg.simbolo || '$') + parts.join(sepDec)
    }

    return (cfg.simbolo || '$') + formatted
  } catch {
    return (cfg.simbolo || '$') + val.toFixed(dec)
  }
}

export function formatNumber(amount: number | string | null | undefined, decimals?: number): string {
  const val = typeof amount === 'string' ? parseFloat(amount) : (amount || 0)
  const d = decimals ?? _monedaConfig.decimales
  const cfg = _monedaConfig

  try {
    const formatted = new Intl.NumberFormat(cfg.locale, {
      style: 'decimal',
      minimumFractionDigits: d,
      maximumFractionDigits: d,
    }).format(val)

    if (cfg.separador_miles && cfg.separador_miles !== getDefaultThousandsSeparator(cfg.locale)) {
      const parts = formatted.split(getDefaultDecimalSeparator(cfg.locale) || '.')
      parts[0] = parts[0].replace(new RegExp('\\' + getDefaultThousandsSeparator(cfg.locale), 'g'), cfg.separador_miles)
      return parts.join(cfg.separador_decimal)
    }

    return formatted
  } catch {
    return val.toFixed(d)
  }
}

export function parseMoney(value: string): number {
  const cfg = _monedaConfig
  let cleaned = value.replace(cfg.simbolo, '').trim()
  if (cfg.separador_miles) cleaned = cleaned.replace(new RegExp('\\' + cfg.separador_miles, 'g'), '')
  if (cfg.separador_decimal) cleaned = cleaned.replace(cfg.separador_decimal, '.')
  return parseFloat(cleaned) || 0
}

export function redondear(subtotal: number): number {
  if (_redondeoMultiplo <= 0) return Math.max(0, subtotal)
  return Math.max(_redondeoMultiplo, Math.ceil(subtotal / _redondeoMultiplo) * _redondeoMultiplo)
}

function getDefaultThousandsSeparator(locale: string): string {
  try {
    const parts = new Intl.NumberFormat(locale).formatToParts(1000)
    return parts.find(p => p.type === 'group')?.value || '.'
  } catch { return '.' }
}

function getDefaultDecimalSeparator(locale: string): string {
  try {
    const parts = new Intl.NumberFormat(locale).formatToParts(1.1)
    return parts.find(p => p.type === 'decimal')?.value || ','
  } catch { return ',' }
}
