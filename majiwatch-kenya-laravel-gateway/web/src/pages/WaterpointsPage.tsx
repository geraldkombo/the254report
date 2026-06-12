import { useMemo, useState } from "react"
import { useQuery } from "@tanstack/react-query"

import { CountyMap } from "../components/CountyMap"
import { api } from "../lib/api"

export function WaterpointsPage() {
  const countiesQ = useQuery({ queryKey: ["counties"], queryFn: api.counties })
  const [county, setCounty] = useState<string>("")
  const [lat, setLat] = useState<string>("0.0")
  const [lng, setLng] = useState<string>("37.9")
  const [lookup, setLookup] = useState<any>(null)
  const [lookupErr, setLookupErr] = useState<string>("")

  const countyOptions = useMemo(() => {
    const arr =
      countiesQ.data?.features
        .map((f) => ({ code: String(f.properties.code), name: String(f.properties.name) }))
        .sort((a, b) => a.name.localeCompare(b.name)) || []
    return arr
  }, [countiesQ.data])

  async function doLookup() {
    setLookup(null)
    setLookupErr("")
    const body = { lat: Number(lat), lng: Number(lng) }
    const res = await fetch(`${api.baseUrl}/lookup/waterpoint`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    })
    if (!res.ok) {
      setLookupErr(`${res.status} ${res.statusText}`)
      return
    }
    setLookup(await res.json())
  }

  return (
    <div className="h-full grid grid-cols-1 xl:grid-cols-[1fr_420px] gap-6">
      <div className="min-h-0 h-[52vh] xl:h-auto">
        <CountyMap metric="composite" showWaterpoints />
      </div>
      <div className="min-h-0 flex flex-col gap-4">
        <div className="rounded-[26px] border border-black/10 bg-[#f7f1e6]/70 p-5">
          <div className="text-[11px] tracking-[0.18em] uppercase font-semibold text-black/60">Exports</div>
          <div className="mt-3 flex flex-col gap-3">
            <div className="flex items-center gap-2">
              <select
                value={county}
                onChange={(e) => setCounty(e.target.value)}
                className="flex-1 rounded-xl border border-black/10 bg-white/70 px-3 py-2 text-[13px] font-semibold text-[#0b1220] outline-none"
              >
                <option value="">All counties</option>
                {countyOptions.map((c) => (
                  <option key={c.code} value={c.code}>
                    {c.name}
                  </option>
                ))}
              </select>
              <a
                className="rounded-xl bg-[#0b1220] text-[#f7f1e6] px-3 py-2 text-[13px] font-semibold"
                href={`${api.baseUrl}/export/waterpoints${county ? `?county=${county}` : ""}`}
              >
                Download CSV
              </a>
            </div>
            <div className="text-[12px] text-black/60">Water points colored by functionality: blue (functioning), amber (partial), red (broken).</div>
          </div>
        </div>

        <div className="flex-1 min-h-0 rounded-[26px] border border-black/10 bg-white/55 p-5 overflow-auto">
          <div className="text-[11px] tracking-[0.18em] uppercase font-semibold text-black/60">Nearest Water Point</div>
          <div className="mt-3 grid grid-cols-2 gap-3">
            <label className="flex flex-col gap-1">
              <span className="text-[11px] font-semibold text-black/60">Latitude</span>
              <input
                value={lat}
                onChange={(e) => setLat(e.target.value)}
                className="rounded-xl border border-black/10 bg-[#f7f1e6]/70 px-3 py-2 text-[13px] font-semibold text-[#0b1220] outline-none"
              />
            </label>
            <label className="flex flex-col gap-1">
              <span className="text-[11px] font-semibold text-black/60">Longitude</span>
              <input
                value={lng}
                onChange={(e) => setLng(e.target.value)}
                className="rounded-xl border border-black/10 bg-[#f7f1e6]/70 px-3 py-2 text-[13px] font-semibold text-[#0b1220] outline-none"
              />
            </label>
          </div>
          <button type="button" onClick={doLookup} className="mt-3 w-full rounded-xl bg-[#1B66FF] text-[#f7f1e6] px-3 py-2 text-[13px] font-semibold">
            Lookup nearest
          </button>

          {lookupErr ? <div className="mt-3 text-[12px] font-semibold text-[#E23B2E]">{lookupErr}</div> : null}
          {lookup ? (
            <div className="mt-3 rounded-2xl border border-black/10 bg-[#0b1220]/95 p-4 text-[#f7f1e6]">
              <div className="text-[11px] tracking-[0.18em] uppercase font-semibold text-[#f7f1e6]/70">Result</div>
              <div className="mt-1 text-[13px] font-semibold">Type: {lookup.type}</div>
              <div className="mt-1 text-[12px] text-[#f7f1e6]/80">Status: {lookup.functionality || "—"}</div>
              <div className="mt-1 text-[12px] text-[#f7f1e6]/80">County: {lookup.county_code || "—"}</div>
              <div className="mt-2 text-[12px] text-[#f7f1e6]/80">Distance: {Number(lookup.distance_m).toFixed(0)} m</div>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  )
}
