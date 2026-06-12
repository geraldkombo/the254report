import { useMemo, useState } from "react"
import { useNavigate } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"

import { CountyMap } from "../components/CountyMap"
import { api } from "../lib/api"
import type { CountyScore } from "../lib/types"

const metrics: Array<{ key: keyof Pick<CountyScore, "composite" | "water_access" | "sanitation" | "water_quality" | "utility_performance" | "governance" | "climate_resilience">; label: string }> =
  [
    { key: "composite", label: "Composite" },
    { key: "water_access", label: "Water Access" },
    { key: "sanitation", label: "Sanitation" },
    { key: "water_quality", label: "Water Quality" },
    { key: "utility_performance", label: "Utility Performance" },
    { key: "governance", label: "Governance" },
    { key: "climate_resilience", label: "Climate Resilience" },
  ]

function median(values: number[]) {
  const sorted = values.slice().sort((a, b) => a - b)
  const mid = Math.floor(sorted.length / 2)
  return sorted.length % 2 === 0 ? (sorted[mid - 1] + sorted[mid]) / 2 : sorted[mid]
}

export function DashboardPage() {
  const nav = useNavigate()
  const [metric, setMetric] = useState<(typeof metrics)[number]["key"]>("composite")

  const scoresQ = useQuery({ queryKey: ["scores", "latest"], queryFn: api.scoresLatest })
  const alertsQ = useQuery({ queryKey: ["alerts"], queryFn: api.alerts, refetchInterval: 60_000 })

  const summary = useMemo(() => {
    const scores = scoresQ.data || []
    const composites = scores.map((s) => s.composite).filter((v) => Number.isFinite(v))
    const m = composites.length ? median(composites) : null
    const watch = (alertsQ.data || []).filter((a) => a.severity === "watch").length
    const warning = (alertsQ.data || []).filter((a) => a.severity === "warning").length
    const emergency = (alertsQ.data || []).filter((a) => a.severity === "emergency").length
    return { medianComposite: m, watch, warning, emergency }
  }, [alertsQ.data, scoresQ.data])

  return (
    <div className="h-full grid grid-cols-1 xl:grid-cols-[1fr_360px] gap-6">
      <div className="min-h-0 h-[58vh] xl:h-auto">
        <CountyMap metric={metric} showWaterpoints selectedCounty={null} onSelectCounty={(code) => nav(`/county/${code}`)} />
      </div>
      <div className="min-h-0 flex flex-col gap-4">
        <div className="rounded-[26px] border border-black/10 bg-[#f7f1e6]/70 p-5 shadow-[0_30px_70px_-55px_rgba(11,18,32,0.65)]">
          <div className="text-[11px] tracking-[0.18em] uppercase font-semibold text-black/60">National Snapshot</div>
          <div className="mt-3 grid grid-cols-2 gap-3">
            <div className="rounded-2xl border border-black/10 bg-white/50 p-4">
              <div className="text-[11px] tracking-[0.18em] uppercase font-semibold text-black/60">Median Composite</div>
              <div className="mt-1 text-[28px] font-semibold text-[#0b1220]">
                {summary.medianComposite === null ? "—" : summary.medianComposite.toFixed(1)}
              </div>
            </div>
            <div className="rounded-2xl border border-black/10 bg-white/50 p-4">
              <div className="text-[11px] tracking-[0.18em] uppercase font-semibold text-black/60">Active Alerts</div>
              <div className="mt-1 text-[12px] font-semibold text-[#0b1220]">
                {summary.emergency} Emergency • {summary.warning} Warning • {summary.watch} Watch
              </div>
              <div className="mt-2 text-[11px] text-black/60">Emergency triggers auto PDF brief.</div>
            </div>
          </div>
        </div>

        <div className="rounded-[26px] border border-black/10 bg-[#0b1220]/95 p-5 text-[#f7f1e6] shadow-[0_30px_70px_-55px_rgba(11,18,32,0.75)]">
          <div className="flex items-center justify-between gap-4">
            <div>
              <div className="text-[11px] tracking-[0.18em] uppercase font-semibold text-[#f7f1e6]/70">Layer</div>
              <div className="mt-1 text-[18px] font-semibold">Score Choropleth</div>
            </div>
            <select
              value={metric}
              onChange={(e) => setMetric(e.target.value as any)}
              className="rounded-xl bg-[#f7f1e6] text-[#0b1220] px-3 py-2 text-[13px] font-semibold outline-none"
            >
              {metrics.map((m) => (
                <option key={m.key} value={m.key}>
                  {m.label}
                </option>
              ))}
            </select>
          </div>
          <div className="mt-3 text-[12px] text-[#f7f1e6]/75">
            Click a county for a briefing. Water points are colored by functionality status.
          </div>
        </div>

        <div className="flex-1 min-h-0 rounded-[26px] border border-black/10 bg-[#f7f1e6]/70 p-5 overflow-auto">
          <div className="flex items-center justify-between gap-3">
            <div className="text-[11px] tracking-[0.18em] uppercase font-semibold text-black/60">Latest Alerts</div>
            <button
              type="button"
              onClick={() => nav("/alerts")}
              className="rounded-full border border-black/15 bg-white/60 px-3 py-1 text-[12px] font-semibold text-[#0b1220] hover:bg-white"
            >
              Open feed
            </button>
          </div>
          <div className="mt-3 space-y-2">
            {(alertsQ.data || []).slice(0, 8).map((a) => (
              <div key={a.id} className="rounded-2xl border border-black/10 bg-white/55 p-3">
                <div className="flex items-center justify-between gap-3">
                  <div className="text-[13px] font-semibold text-[#0b1220]">{a.county_code}</div>
                  <span
                    className={[
                      "rounded-full px-2 py-1 text-[11px] font-semibold uppercase tracking-[0.12em]",
                      a.severity === "emergency"
                        ? "bg-[#E23B2E] text-[#f7f1e6]"
                        : a.severity === "warning"
                          ? "bg-[#F6B42C] text-[#0b1220]"
                          : "bg-black/10 text-[#0b1220]",
                    ].join(" ")}
                  >
                    {a.severity}
                  </span>
                </div>
                <div className="mt-1 text-[12px] text-black/70">{a.message}</div>
              </div>
            ))}
            {alertsQ.data && alertsQ.data.length === 0 ? (
              <div className="text-[12px] text-black/60">No active alerts.</div>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  )
}
