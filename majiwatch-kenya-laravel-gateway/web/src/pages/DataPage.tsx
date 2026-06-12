import { useMemo, useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { api } from "../lib/api"
import { getApiKey, setApiKey } from "../lib/settings"

type Datasource = { id: string; name: string; license: string | null; homepage: string | null }

async function fetchDatasources(): Promise<Datasource[]> {
  const res = await fetch(`${api.baseUrl}/datasources`)
  if (!res.ok) throw new Error("Failed to load datasources")
  return (await res.json()) as Datasource[]
}

export function DataPage() {
  const qc = useQueryClient()
  const sourcesQ = useQuery({ queryKey: ["datasources"], queryFn: fetchDatasources })
  const [apiKey, setKey] = useState(getApiKey())
  const [year, setYear] = useState(String(new Date().getUTCFullYear()))
  const [period, setPeriod] = useState(new Date().toISOString().slice(0, 10))

  const computeM = useMutation({
    mutationFn: async () => {
      const key = apiKey.trim()
      if (!key) throw new Error("API key required")
      return api.compute(Number(year), period, key)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["scores"] })
      qc.invalidateQueries({ queryKey: ["alerts"] })
    },
  })

  const sources = useMemo(() => sourcesQ.data || [], [sourcesQ.data])

  function saveKey() {
    setApiKey(apiKey.trim())
    setKey(apiKey.trim())
  }

  return (
    <div className="h-full grid grid-cols-1 xl:grid-cols-[1fr_420px] gap-6">
      <div className="min-h-0 rounded-[28px] border border-black/10 bg-white/55 overflow-auto">
        <div className="p-5 border-b border-black/10">
          <div className="text-[11px] tracking-[0.18em] uppercase font-semibold text-black/60">Datasets</div>
          <div className="mt-1 text-[12px] text-black/60">
            This build ships with a deterministic baseline bundle for immediate usability, plus connectors for key public sources.
          </div>
        </div>
        <div className="p-5 space-y-3">
          {sources.map((s) => (
            <div key={s.id} className="rounded-[22px] border border-black/10 bg-[#f7f1e6]/70 p-4">
              <div className="text-[13px] font-semibold text-[#0b1220]">{s.name}</div>
              <div className="mt-1 text-[12px] text-black/70">ID: {s.id}</div>
              <div className="mt-1 text-[12px] text-black/60">{s.license || "License: —"}</div>
              {s.homepage ? (
                <a className="mt-2 inline-block text-[12px] font-semibold text-[#1B66FF]" href={s.homepage} target="_blank" rel="noreferrer">
                  Source link
                </a>
              ) : null}
            </div>
          ))}
          {sourcesQ.isLoading ? <div className="text-[12px] text-black/60">Loading…</div> : null}
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
        </div>

        <div className="rounded-[26px] border border-black/10 bg-[#f7f1e6]/70 p-5">
          <div className="text-[11px] tracking-[0.18em] uppercase font-semibold text-black/60">Manual Compute</div>
          <div className="mt-3 grid grid-cols-2 gap-3">
            <label className="flex flex-col gap-1">
              <span className="text-[11px] font-semibold text-black/60">Year</span>
              <input
                value={year}
                onChange={(e) => setYear(e.target.value)}
                className="rounded-xl border border-black/10 bg-white/70 px-3 py-2 text-[13px] font-semibold text-[#0b1220] outline-none"
              />
            </label>
            <label className="flex flex-col gap-1">
              <span className="text-[11px] font-semibold text-black/60">Period</span>
              <input
                value={period}
                onChange={(e) => setPeriod(e.target.value)}
                className="rounded-xl border border-black/10 bg-white/70 px-3 py-2 text-[13px] font-semibold text-[#0b1220] outline-none"
              />
            </label>
          </div>
          <button
            type="button"
            onClick={() => computeM.mutate()}
            className="mt-3 w-full rounded-xl bg-[#0b1220] text-[#f7f1e6] px-3 py-2 text-[13px] font-semibold disabled:opacity-60"
            disabled={computeM.isPending}
          >
            {computeM.isPending ? "Computing…" : "Run compute now"}
          </button>
          {computeM.isError ? <div className="mt-2 text-[12px] font-semibold text-[#E23B2E]">{String(computeM.error)}</div> : null}
          {computeM.data ? (
            <div className="mt-2 text-[12px] font-semibold text-[#0b1220]">Enqueued task: {computeM.data.task_id || "—"}</div>
          ) : null}
        </div>

        <div className="flex-1 min-h-0 rounded-[26px] border border-black/10 bg-white/55 p-5 overflow-auto">
          <div className="text-[11px] tracking-[0.18em] uppercase font-semibold text-black/60">Exports</div>
          <div className="mt-3 flex flex-wrap gap-2">
            <a
              className="rounded-full bg-[#1B66FF] text-[#f7f1e6] px-3 py-1.5 text-[12px] font-semibold"
              href={`${api.baseUrl}/export/scores?year=${new Date().getUTCFullYear()}`}
            >
              Scores CSV (year)
            </a>
            <a className="rounded-full bg-[#0b1220] text-[#f7f1e6] px-3 py-1.5 text-[12px] font-semibold" href={`${api.baseUrl}/export/waterpoints`}>
              Water points CSV
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}
