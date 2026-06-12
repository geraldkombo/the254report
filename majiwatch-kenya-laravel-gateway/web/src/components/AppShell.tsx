import { useEffect, useMemo, useState } from "react"
import type { ReactNode } from "react"
import { NavLink, useLocation } from "react-router-dom"

const navItems = [
  { to: "/", label: "Dashboard" },
  { to: "/waterpoints", label: "Water Points" },
  { to: "/alerts", label: "Alerts" },
  { to: "/data", label: "Data" },
  { to: "/api", label: "API" },
]

export function AppShell(props: { children: ReactNode }) {
  const location = useLocation()
  const [online, setOnline] = useState(typeof navigator === "undefined" ? true : navigator.onLine)
  const title = useMemo(() => {
    const match = navItems.find((n) => n.to !== "/" && location.pathname.startsWith(n.to)) ?? navItems[0]
    return match.label
  }, [location.pathname])

  useEffect(() => {
    function on() {
      setOnline(true)
    }
    function off() {
      setOnline(false)
    }
    window.addEventListener("online", on)
    window.addEventListener("offline", off)
    return () => {
      window.removeEventListener("online", on)
      window.removeEventListener("offline", off)
    }
  }, [])

  return (
    <div className="h-full bg-[radial-gradient(circle_at_20%_0%,rgba(27,102,255,0.10),transparent_40%),radial-gradient(circle_at_90%_20%,rgba(192,106,59,0.10),transparent_45%),linear-gradient(180deg,#f7f1e6,#f4eddf)]">
      <div className="h-full md:grid md:grid-cols-[260px_1fr]">
        <aside className="hidden md:block h-full border-r border-black/10 bg-black/5 backdrop-blur-sm">
          <div className="px-5 pt-6 pb-5">
            <div className="text-[11px] tracking-[0.26em] uppercase font-semibold text-black/60">MajiWatch Kenya</div>
            <div className="mt-1 text-[22px] leading-tight font-semibold text-[#0b1220]">Water & Sanitation Intelligence</div>
            <div className="mt-2 text-[12px] text-black/60">Kenya • County-level signals</div>
          </div>
          <nav className="px-3 pb-6">
            {navItems.map((n) => (
              <NavLink
                key={n.to}
                to={n.to}
                className={({ isActive }) =>
                  [
                    "block px-3 py-2.5 rounded-xl text-[13px] font-medium transition",
                    isActive ? "bg-[#0b1220] text-[#f7f1e6]" : "text-[#0b1220] hover:bg-black/10",
                  ].join(" ")
                }
                end={n.to === "/"}
              >
                {n.label}
              </NavLink>
            ))}
          </nav>
          <div className="px-5 pb-6">
            <div className="rounded-2xl border border-black/10 bg-[#f7f1e6]/70 p-4">
              <div className="text-[11px] tracking-[0.18em] uppercase font-semibold text-black/60">Status</div>
              <div className="mt-1 text-[12px] text-black/70">
                Use the Data page to trigger a manual refresh and to download exports.
              </div>
            </div>
          </div>
        </aside>
        <main className="h-full min-w-0">
          <div className="h-full flex flex-col">
            <header className="px-4 md:px-7 pt-4 md:pt-6 pb-4">
              <div className="flex items-end justify-between gap-6">
                <div>
                  <div className="text-[11px] tracking-[0.22em] uppercase font-semibold text-black/60">{title}</div>
                  <div className="mt-1 text-[22px] md:text-[28px] font-semibold text-[#0b1220] leading-tight">{title}</div>
                </div>
                <div className="hidden xl:flex items-center gap-2">
                  <span className={["text-[11px] tracking-[0.18em] uppercase font-semibold", online ? "text-black/60" : "text-[#E23B2E]"].join(" ")}>
                    {online ? "Online" : "Offline"}
                  </span>
                  <span className="text-[11px] tracking-[0.18em] uppercase font-semibold text-black/60">Composite</span>
                  <span className="inline-flex items-center rounded-full bg-black/10 px-2.5 py-1 text-[12px] font-semibold text-[#0b1220]">
                    0–100
                  </span>
                </div>
              </div>
            </header>
            <div className="flex-1 min-h-0 px-4 md:px-7 pb-24 md:pb-7">{props.children}</div>
          </div>
        </main>
      </div>

      <nav className="md:hidden fixed bottom-0 left-0 right-0 border-t border-black/10 bg-[#f7f1e6]/92 backdrop-blur">
        <div className="px-2 py-2 grid grid-cols-5 gap-2">
          {navItems.map((n) => (
            <NavLink
              key={n.to}
              to={n.to}
              className={({ isActive }) =>
                [
                  "text-center rounded-2xl py-2 text-[11px] font-semibold transition",
                  isActive ? "bg-[#0b1220] text-[#f7f1e6]" : "text-[#0b1220] bg-black/5",
                ].join(" ")
              }
              end={n.to === "/"}
            >
              {n.label}
            </NavLink>
          ))}
        </div>
      </nav>
    </div>
  )
}
