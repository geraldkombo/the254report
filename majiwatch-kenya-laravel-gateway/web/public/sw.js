const CACHE_STATIC = "maji-static-v1"
const CACHE_RUNTIME = "maji-runtime-v1"

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches
      .open(CACHE_STATIC)
      .then((cache) =>
        cache.addAll([
          "/app/",
          "/app/index.html",
          "/app/manifest.webmanifest",
          "/app/favicon.svg",
          "/app/styles/offline.json",
        ])
      )
      .then(() => self.skipWaiting())
  )
})

self.addEventListener("activate", (event) => {
  event.waitUntil(self.clients.claim())
})

function isApi(url) {
  return (
    url.pathname.startsWith("/api/counties") ||
    url.pathname.startsWith("/api/scores") ||
    url.pathname.startsWith("/api/alerts") ||
    url.pathname.startsWith("/api/tiles/") ||
    url.pathname.startsWith("/reports/")
  )
}

self.addEventListener("fetch", (event) => {
  const req = event.request
  const url = new URL(req.url)

  if (req.method !== "GET") return

  if (req.mode === "navigate") {
    event.respondWith(
      caches.match("/app/index.html").then((cached) => cached || fetch(req))
    )
    return
  }

  if (url.origin !== self.location.origin) return

  if (isApi(url)) {
    event.respondWith(
      caches.open(CACHE_RUNTIME).then(async (cache) => {
        const cached = await cache.match(req)
        const fetchPromise = fetch(req)
          .then((res) => {
            if (res && res.ok) cache.put(req, res.clone())
            return res
          })
          .catch(() => undefined)
        return cached || (await fetchPromise) || new Response("", { status: 504 })
      })
    )
    return
  }

  event.respondWith(
    caches.match(req).then((cached) => {
      if (cached) return cached
      return caches.open(CACHE_RUNTIME).then((cache) =>
        fetch(req).then((res) => {
          if (res && res.ok) cache.put(req, res.clone())
          return res
        })
      )
    })
  )
})
