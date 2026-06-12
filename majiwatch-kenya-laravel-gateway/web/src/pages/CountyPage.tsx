import { useMemo } from "react"
import { useQuery } from "@tanstack/react-query"
import { useNavigate, useParams } from "react-router-dom"

import { CountyMap } from "../components/CountyMap"
import { api } from "../lib/api"

export function CountyPage() {
  const params = useParams()
  const code = params.code || ""
  const nav = useNavigate()

  const countiesQ = useQuery({ queryKey: ["counties"], queryFn: api.counties })
  const scoreQ = useQuery({ queryKey: ["scores", code], queryFn: () => apiGetScore(code), enabled: !!code })

  const countyName = useMemo(() => {
    const f = countiesQ.data?.features.find((x) => String(x.properties.code) === code)
    return (f?.properties.name as string) || code
  }, [code, countiesQ.data])

  return (
    <div className="h-full grid grid-cols-1 xl:grid-cols-[1fr_420px] gap-6">
      <div className="min-h-0 h-[52vh] xl:h-auto">
        <CountyMap metric="composite" selectedCounty={code} onSelectCounty={(c) => nav(`/county/${c}`)} />
      </div>
      <div className="min-h-0 flex flex-col gap-4">
        <div className="rounded-[26px] border border-black/10 bg-[#f7f1e6]/70 p-5">
          <div className="text-[11px] tracking-[0.18em] uppercase font-semibold text-black/60">County</div>
          <div className="mt-1 text-[22px] font-semibold text-[#0b1220]">{countyName}</div>
          <div className="mt-1 text-[12px] text-black/60">Code: {code}</div>
        </div>

        <div className="flex-1 min-h-0 rounded-[26px] border border-black/10 bg-white/55 p-5 overflow-auto">
          <div className="text-[11px] tracking-[0.18em] uppercase font-semibold text-black/60">Latest Scores</div>
          <div className="mt-3 grid grid-cols-2 gap-3">
            <ScoreTile label="Composite" value={scoreQ.data?.composite} variant="composite" />
            <ScoreTile label="Water Access" value={scoreQ.data?.water_access} />
            <ScoreTile label="Sanitation" value={scoreQ.data?.sanitation} />
            <ScoreTile label="Water Quality" value={scoreQ.data?.water_quality} />
            <ScoreTile label="Utility" value={scoreQ.data?.utility_performance} />
            <ScoreTile label="Governance" value={scoreQ.data?.governance} />
            <ScoreTile label="Resilience" value={scoreQ.data?.climate_resilience} />
            <ScoreTile label="Confidence" value={scoreQ.data?.confidence} />
          </div>

          <div className="mt-5 rounded-2xl border border-black/10 bg-[#0b1220]/95 p-4 text-[#f7f1e6]">
            <div className="text-[11px] tracking-[0.18em] uppercase font-semibold text-[#f7f1e6]/70">Exports</div>
            <div className="mt-2 flex flex-wrap gap-2">
              <a
                className="rounded-full bg-[#f7f1e6] text-[#0b1220] px-3 py-1.5 text-[12px] font-semibold"
                href={`${api.baseUrl}/export/waterpoints?county=${code}`}
              >
                Water points CSV
              </a>
              <a
                className="rounded-full bg-[#f7f1e6] text-[#0b1220] px-3 py-1.5 text-[12px] font-semibold"
                href={`${api.baseUrl}/export/scores?year=${new Date().getUTCFullYear()}`}
              >
                Scores CSV (year)
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function ScoreTile(props: { label: string; value: number | undefined; variant?: "composite" }) {
  const v = props.value
  const color =
    props.variant === "composite"
      ? v === undefined
        ? "text-black/60"
        : v < 30
          ? "text-[#E23B2E]"
          : v < 45
            ? "text-[#F6B42C]"
            : v < 60
              ? "text-[#C06A3B]"
              : "text-[#1B66FF]"
      : "text-[#0b1220]"

  return (
    <div className="rounded-2xl border border-black/10 bg-[#f7f1e6]/70 p-4">
      <div className="text-[11px] tracking-[0.18em] uppercase font-semibold text-black/60">{props.label}</div>
      <div className={["mt-1 text-[22px] font-semibold", color].join(" ")}>{v === undefined ? "—" : v.toFixed(1)}</div>
    </div>
  )
}

async function apiGetScore(code: string) {
  const res = await fetch(`${api.baseUrl}/scores/${code}`)
  if (!res.ok) throw new Error("Score fetch failed")
  return (await res.json()) as any
}
