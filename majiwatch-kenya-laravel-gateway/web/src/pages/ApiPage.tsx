import { api } from "../lib/api"

export function ApiPage() {
  return (
    <div className="h-full rounded-[28px] overflow-hidden border border-black/10 bg-white/55">
      <iframe title="API Docs" src={`${api.baseUrl}/docs`} className="h-full w-full" />
    </div>
  )
}

