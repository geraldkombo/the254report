import maplibregl from "maplibre-gl"
import type { Map as MapLibreMap } from "maplibre-gl"
import { useEffect, useMemo, useRef, useState } from "react"

import { api } from "../lib/api"
import type { CountyScore, GeoJsonFeatureCollection } from "../lib/types"

const styleUrl = "https://demotiles.maplibre.org/style.json"
const offlineStyleUrl = "/app/styles/offline.json"

function hasWebGL() {
  if (typeof document === "undefined") return true
  const c = document.createElement("canvas")
  const gl = c.getContext("webgl2") || c.getContext("webgl") || c.getContext("experimental-webgl")
  return !!gl
}

function colorForScore(v: number) {
  if (v < 30) return "#E23B2E"
  if (v < 45) return "#F6B42C"
  if (v < 60) return "#C06A3B"
  if (v < 75) return "#4F8A6D"
  return "#1B66FF"
}

export function CountyMap(props: {
  metric: keyof Pick<
    CountyScore,
    | "composite"
    | "water_access"
    | "sanitation"
    | "water_quality"
    | "utility_performance"
    | "governance"
    | "climate_resilience"
  >
  showWaterpoints?: boolean
  selectedCounty?: string | null
  onSelectCounty?: (code: string) => void
}) {
  const containerRef = useRef<HTMLDivElement | null>(null)
  const mapRef = useRef<MapLibreMap | null>(null)
  const [hover, setHover] = useState<{ code: string; name: string; score: number } | null>(null)
  const [data, setData] = useState<{ counties: GeoJsonFeatureCollection; scores: CountyScore[] } | null>(null)
  const [webglOk] = useState(hasWebGL())

  const joined = useMemo(() => {
    if (!data) return null
    const scoreByCounty = new globalThis.Map<string, CountyScore>()
    data.scores.forEach((s) => scoreByCounty.set(s.county_code, s))
    const fc: GeoJsonFeatureCollection = {
      type: "FeatureCollection",
      features: data.counties.features.map((f) => {
        const code = String(f.properties.code)
        const s = scoreByCounty.get(code)
        return {
          ...f,
          properties: {
            ...f.properties,
            score: s ? Number(s[props.metric]) : null,
            composite: s ? Number(s.composite) : null,
          },
        }
      }),
    }
    return fc
  }, [data, props.metric])

  useEffect(() => {
    let canceled = false
    Promise.all([api.counties(), api.scoresLatest()])
      .then(([counties, scores]) => {
        if (canceled) return
        setData({ counties, scores })
      })
      .catch(() => {})
    return () => {
      canceled = true
    }
  }, [])

  useEffect(() => {
    if (!containerRef.current) return
    if (!webglOk) return
    if (mapRef.current) return

    const map = new maplibregl.Map({
      container: containerRef.current,
      style: styleUrl,
      center: [37.9, 0.2],
      zoom: 5.2,
      attributionControl: false,
    })
    mapRef.current = map

    map.addControl(new maplibregl.AttributionControl({ compact: true }))

    let didFallback = false
    map.on("error", () => {
      if (didFallback) return
      didFallback = true
      try {
        map.setStyle(offlineStyleUrl)
      } catch {
        return
      }
    })

    map.on("load", () => {
      map.addSource("counties", { type: "geojson", data: { type: "FeatureCollection", features: [] } })
      map.addLayer({
        id: "counties-fill",
        type: "fill",
        source: "counties",
        paint: {
          "fill-color": ["case", ["has", "score"], ["get", "color"], "#D8D0C6"],
          "fill-opacity": 0.62,
        },
      })
      map.addLayer({
        id: "counties-outline",
        type: "line",
        source: "counties",
        paint: { "line-color": "rgba(11,18,32,0.42)", "line-width": 1 },
      })

      map.on("mousemove", "counties-fill", (e) => {
        const f = e.features?.[0]
        if (!f) return
        const code = String(f.properties?.code || "")
        const name = String(f.properties?.name || "")
        const score = Number(f.properties?.score ?? NaN)
        if (!code) return
        if (Number.isFinite(score)) setHover({ code, name, score })
        else setHover({ code, name, score: NaN })
      })
      map.on("mouseleave", "counties-fill", () => setHover(null))

      map.on("click", "counties-fill", (e) => {
        const f = e.features?.[0]
        const code = String(f?.properties?.code || "")
        if (code && props.onSelectCounty) props.onSelectCounty(code)
      })

      if (props.showWaterpoints) {
        map.addSource("waterpoints", {
          type: "vector",
          tiles: [`${api.baseUrl}/tiles/waterpoints/{z}/{x}/{y}.pbf`],
          minzoom: 0,
          maxzoom: 14,
        })
        map.addLayer({
          id: "waterpoints-circle",
          type: "circle",
          source: "waterpoints",
          "source-layer": "waterpoints",
          paint: {
            "circle-color": [
              "match",
              ["get", "functionality"],
              "functioning",
              "#1B66FF",
              "partially_functioning",
              "#F6B42C",
              "broken",
              "#E23B2E",
              "#0B1220",
            ],
            "circle-radius": ["interpolate", ["linear"], ["zoom"], 5, 2, 8, 4, 11, 7],
            "circle-stroke-width": 1,
            "circle-stroke-color": "rgba(11,18,32,0.55)",
            "circle-opacity": 0.9,
          },
        })
      }
    })

    return () => {
      map.remove()
      mapRef.current = null
    }
  }, [props.onSelectCounty, props.showWaterpoints])

  useEffect(() => {
    const map = mapRef.current
    if (!map) return
    if (!map.isStyleLoaded()) return
    if (!joined) return
    const fc = {
      type: "FeatureCollection",
      features: joined.features.map((f) => {
        const s = Number(f.properties.score)
        return { ...f, properties: { ...f.properties, color: Number.isFinite(s) ? colorForScore(s) : "#D8D0C6" } }
      }),
    }
    const src = map.getSource("counties") as any
    if (src) src.setData(fc)
  }, [joined])

  return (
    <div className="relative h-full w-full overflow-hidden rounded-[28px] border border-black/10 bg-black/5 shadow-[0_30px_70px_-55px_rgba(11,18,32,0.65)]">
      {webglOk ? (
        <div ref={containerRef} className="h-full w-full" />
      ) : (
        <div className="h-full w-full flex items-center justify-center bg-[#f7f1e6]">
          <div className="max-w-[520px] px-6 text-center">
            <div className="text-[12px] tracking-[0.18em] uppercase font-semibold text-black/60">Map Unavailable</div>
            <div className="mt-2 text-[16px] font-semibold text-[#0b1220]">Your device/browser does not support WebGL.</div>
            <div className="mt-2 text-[12px] text-black/60">
              The dashboard still works for scores and alerts. For full map features, use a WebGL-enabled browser.
            </div>
          </div>
        </div>
      )}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-4 top-4 rounded-2xl border border-black/10 bg-[#f7f1e6]/80 px-3 py-2 backdrop-blur">
          <div className="text-[11px] tracking-[0.18em] uppercase font-semibold text-black/60">Map</div>
          <div className="text-[12px] font-semibold text-[#0b1220]">County choropleth • {props.metric.replace("_", " ")}</div>
        </div>
        {hover ? (
          <div className="absolute right-4 top-4 w-[280px] rounded-2xl border border-black/10 bg-[#0b1220]/90 p-3 text-[#f7f1e6] backdrop-blur">
            <div className="text-[11px] tracking-[0.18em] uppercase font-semibold text-[#f7f1e6]/70">County</div>
            <div className="mt-0.5 text-[16px] font-semibold">{hover.name}</div>
            <div className="mt-2 flex items-center justify-between">
              <div className="text-[11px] tracking-[0.18em] uppercase font-semibold text-[#f7f1e6]/70">Score</div>
              <div className="text-[18px] font-semibold">{Number.isFinite(hover.score) ? hover.score.toFixed(1) : "—"}</div>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  )
}
