import { lazy, Suspense } from "react"
import { Navigate, Route, Routes } from "react-router-dom"

import { AppShell } from "./components/AppShell"

const DashboardPage = lazy(() => import("./pages/DashboardPage").then((m) => ({ default: m.DashboardPage })))
const CountyPage = lazy(() => import("./pages/CountyPage").then((m) => ({ default: m.CountyPage })))
const WaterpointsPage = lazy(() => import("./pages/WaterpointsPage").then((m) => ({ default: m.WaterpointsPage })))
const AlertsPage = lazy(() => import("./pages/AlertsPage").then((m) => ({ default: m.AlertsPage })))
const DataPage = lazy(() => import("./pages/DataPage").then((m) => ({ default: m.DataPage })))
const ApiPage = lazy(() => import("./pages/ApiPage").then((m) => ({ default: m.ApiPage })))

export function App() {
  return (
    <AppShell>
      <Suspense fallback={<div className="text-[12px] font-semibold text-black/60">Loading…</div>}>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/county/:code" element={<CountyPage />} />
          <Route path="/waterpoints" element={<WaterpointsPage />} />
          <Route path="/alerts" element={<AlertsPage />} />
          <Route path="/data" element={<DataPage />} />
          <Route path="/api" element={<ApiPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Suspense>
    </AppShell>
  )
}

export default App
