export type GeoJsonFeatureCollection = {
  type: "FeatureCollection"
  features: Array<{
    type: "Feature"
    geometry: any
    properties: Record<string, any>
  }>
}

export type CountyScore = {
  county_code: string
  year: number
  period: string
  water_access: number
  sanitation: number
  water_quality: number
  utility_performance: number
  governance: number
  climate_resilience: number
  composite: number
  confidence: number
  computed_at: string
}

export type Alert = {
  id: string
  county_code: string
  severity: "watch" | "warning" | "emergency" | string
  rule: string
  message: string
  triggered_at: string
  resolved_at: string | null
  pdf_report_url: string | null
}

