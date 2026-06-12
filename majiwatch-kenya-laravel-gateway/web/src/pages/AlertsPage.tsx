import { useMemo, useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { api } from "../lib/api"
import { getApiKey, setApiKey } from "../lib/settings"

export function AlertsPage() {
  const qc = useQueryClient()
  const alertsQ = useQuery({ queryKey: ["alerts"], queryFn: api.alerts, refetchInterval: 60_000 })

  const [apiKey, setKey] = useState(getApiKey())
  const [filter, setFilter] = useState<"all" | "emergency" | "warning" | "watch">("all")

  const filtered = useMemo(() => {
    const items = alertsQ.data || []
    if (filter === "all") return items
    return items.filter((a) => a.severity === filter)
  }, [alertsQ.data, filter])

  const resolveM = useMutation({
    mutationFn: async (id: string) => {
      const key = apiKey.trim()
      if (!key) throw new Error("API key required")
      const r = await api.resolveAlert(id, key)
      return r
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["alerts"] })
    },
  })

  function saveKey() {
    setApiKey(apiKey.trim())
    setKey(apiKey.trim())
  }

  return (
    <div className="h-full grid grid-cols-1 xl:grid-cols-[1fr_420px] gap-6">
      <div className="min-h-0 rounded-[28px] border border-black/10 bg-white/55 overflow-auto">
        <div className="p-5 border-b border-black/10 flex items-center justify-between gap-4">
          <div>
            <div className="text-[11px] tracking-[0.18em] uppercase font-semibold text-black/60">Active Alerts</div>
            <div className="mt-1 text-[12px] text-black/60">Resolve requires an API key.</div>
          </div>
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as any)}
            className="rounded-xl border border-black/10 bg-[#f7f1e6]/70 px-3 py-2 text-[13px] font-semibold text-[#0b1220] outline-none"
          >
            <option value="all">All</option>
            <option value="emergency">Emergency</option>
            <option value="warning">Warning</option>
            <option value="watch">Watch</option>
          </select>
        </div>

        <div className="p-5 space-y-3">
          {filtered.map((a) => (
            <div key={a.id} className="rounded-[22px] border border-black/10 bg-[#f7f1e6]/70 p-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="text-[14px] font-semibold text-[#0b1220]">County {a.county_code}</div>
                  <div className="mt-1 text-[12px] text-black/70">{a.message}</div>
                </div>
                <span
                  className={[
                    "rounded-full px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.12em] shrink-0",
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

              <div className="mt-3 flex flex-wrap items-center gap-2">
                {a.pdf_report_url ? (
                  <a
                    href={a.pdf_report_url}
                    className="rounded-full bg-[#0b1220] text-[#f7f1e6] px-3 py-1.5 text-[12px] font-semibold"
                    target="_blank"
                    rel="noreferrer"
                  >
                    Open PDF
                  </a>
                ) : null}
                <button
                  type="button"
                  onClick={() => resolveM.mutate(a.id)}
                  className="rounded-full border border-black/10 bg-white/60 px-3 py-1.5 text-[12px] font-semibold text-[#0b1220] hover:bg-white disabled:opacity-50"
                  disabled={resolveM.isPending}
                >
                  Resolve
                </button>
                {resolveM.isError ? (
                  <span className="text-[12px] font-semibold text-[#E23B2E]">{String(resolveM.error)}</span>
                ) : null}
              </div>
            </div>
          ))}
          {filtered.length === 0 ? <div className="text-[12px] text-black/60">No active alerts.</div> : null}
        </div>
      </div>

      <div className="min-h-0 flex flex-col gap-4">
        <div className="rounded-[26px] border border-black/10 bg-[#0b1220]/95 p-5 text-[#f7f1e6]">
          <div className="text-[11px] tracking-[0.18em] uppercase font-semibold text-[#f7f1e6]/70">Operator Key</div>
          <div className="mt-2 flex gap-2">
            <input
              value={apiKey}
              onChange={(e) => setKey(e.target.value)}
              placeholder="X-API-Key"
              className="flex-1 rounded-xl bg-[#f7f1e6] text-[#0b1220] px-3 py-2 text-[13px] font-semibold outline-none"
            />
            <button type="button" onClick={saveKey} className="rounded-xl bg-[#1B66FF] px-3 py-2 text-[13px] font-semibold">
              Save
            </button>
          </div>
          <div className="mt-2 text-[12px] text-[#f7f1e6]/70">
            Stored locally in your browser. Set the same key in the server .env file.
          </div>
        </div>

        <div className="flex-1 min-h-0 rounded-[26px] border border-black/10 bg-white/55 p-5 overflow-auto">
          <div className="text-[11px] tracking-[0.18em] uppercase font-semibold text-black/60">Notes</div>
          <div className="mt-2 text-[12px] text-black/70">
            Emergency alerts automatically generate a PDF county brief. Warning and Watch alerts remain active until resolved.
          </div>
        </div>
      </div>
    </div>
  )
}
