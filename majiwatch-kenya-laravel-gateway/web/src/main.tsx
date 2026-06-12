import "maplibre-gl/dist/maplibre-gl.css"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { StrictMode } from "react"
import { createRoot } from "react-dom/client"
import { BrowserRouter } from "react-router-dom"

import "./index.css"
import App from "./App"

const queryClient = new QueryClient()

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter basename="/app">
        <App />
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>
)

if ("serviceWorker" in navigator) {
  const swUrl = `${import.meta.env.BASE_URL}sw.js`
  navigator.serviceWorker.register(swUrl).catch(() => {})
}
