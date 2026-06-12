<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta name="csrf-token" content="{{ csrf_token() }}">
        <title>MajiWatch Kenya — Water & Sanitation Intelligence</title>
        <meta name="description" content="Mobile-first water & sanitation intelligence for Kenya: county scores, alerts, and audit-ready briefs.">
        <link rel="canonical" href="{{ rtrim(config('app.url'), '/') }}/">
        <meta property="og:title" content="MajiWatch Kenya">
        <meta property="og:description" content="County-level water & sanitation intelligence for Kenya (47 counties).">
        <meta property="og:type" content="website">
        <meta property="og:url" content="{{ rtrim(config('app.url'), '/') }}/">
        <meta property="og:image" content="{{ rtrim(config('app.url'), '/') }}/app/favicon.svg">
        @vite(['resources/css/app.css', 'resources/js/app.js'])
    </head>
    <body class="antialiased bg-gray-950 text-gray-100">
        <div class="min-h-screen">
            <div class="max-w-6xl mx-auto px-6 py-14">
                <div class="flex items-center justify-between gap-6 flex-wrap">
                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 rounded-2xl bg-gradient-to-br from-blue-500 via-gray-900 to-red-500"></div>
                        <div class="font-extrabold tracking-tight text-xl">MajiWatch Kenya</div>
                    </div>
                    <div class="flex items-center gap-3">
                        @auth
                            <a href="/admin" class="inline-flex items-center rounded-xl bg-white/10 px-4 py-2 text-sm font-semibold hover:bg-white/15">Admin</a>
                            <a href="/app/" class="inline-flex items-center rounded-xl bg-blue-500 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-600">Open Dashboard</a>
                        @else
                            <a href="/login" class="inline-flex items-center rounded-xl bg-white/10 px-4 py-2 text-sm font-semibold hover:bg-white/15">Login</a>
                            <a href="/register" class="inline-flex items-center rounded-xl bg-white/10 px-4 py-2 text-sm font-semibold hover:bg-white/15">Register</a>
                            <a href="/app/" class="inline-flex items-center rounded-xl bg-blue-500 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-600">Open Dashboard</a>
                        @endauth
                    </div>
                </div>

                <div class="mt-14 grid grid-cols-1 lg:grid-cols-12 gap-10 items-start">
                    <div class="lg:col-span-7">
                        <h1 class="text-4xl sm:text-5xl font-extrabold tracking-tight leading-[1.05]">
                            Water &amp; Sanitation Intelligence
                            <span class="block text-white/70 mt-2">for Kenya’s 47 counties</span>
                        </h1>
                        <p class="mt-6 text-base sm:text-lg text-white/70 leading-relaxed">
                            MajiWatch Kenya turns public evidence into actionable county signals: nightly scores (0–100), watch/warning/emergency thresholds, and auditable briefs.
                            Built for low bandwidth, mobile-first reality, and operational accountability.
                        </p>

                        <div class="mt-8 flex flex-col sm:flex-row gap-3">
                            <a href="/app/" class="inline-flex items-center justify-center rounded-2xl bg-blue-500 px-5 py-3 text-sm font-semibold text-white hover:bg-blue-600">
                                Launch Dashboard
                            </a>
                            <a href="/api/docs" class="inline-flex items-center justify-center rounded-2xl bg-white/10 px-5 py-3 text-sm font-semibold hover:bg-white/15">
                                API Docs
                            </a>
                            <a href="mailto:{{ env('ADMIN_EMAIL', 'geraldshikunyi@gmail.com') }}" class="inline-flex items-center justify-center rounded-2xl bg-white/10 px-5 py-3 text-sm font-semibold hover:bg-white/15">
                                Contact
                            </a>
                        </div>

                        <div class="mt-10 grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div class="rounded-2xl bg-white/5 border border-white/10 p-5">
                                <div class="text-xs tracking-[0.18em] uppercase font-semibold text-white/50">Scores</div>
                                <div class="mt-2 font-semibold">Access • Sanitation • Quality • Utility • Governance • Resilience</div>
                                <div class="mt-2 text-sm text-white/60">Composite weighted index with confidence.</div>
                            </div>
                            <div class="rounded-2xl bg-white/5 border border-white/10 p-5">
                                <div class="text-xs tracking-[0.18em] uppercase font-semibold text-white/50">Alerts</div>
                                <div class="mt-2 font-semibold">Watch • Warning • Emergency</div>
                                <div class="mt-2 text-sm text-white/60">Emergency generates an evidence-backed brief.</div>
                            </div>
                            <div class="rounded-2xl bg-white/5 border border-white/10 p-5">
                                <div class="text-xs tracking-[0.18em] uppercase font-semibold text-white/50">Mobile-first</div>
                                <div class="mt-2 font-semibold">Fast maps on phones</div>
                                <div class="mt-2 text-sm text-white/60">Vector tiles + offline fallback behavior.</div>
                            </div>
                            <div class="rounded-2xl bg-white/5 border border-white/10 p-5">
                                <div class="text-xs tracking-[0.18em] uppercase font-semibold text-white/50">Open</div>
                                <div class="mt-2 font-semibold">Free and self-hostable</div>
                                <div class="mt-2 text-sm text-white/60">Docker Compose deploy; safe-by-default settings.</div>
                            </div>
                        </div>
                    </div>

                    <div class="lg:col-span-5">
                        <div class="rounded-3xl border border-white/10 bg-gradient-to-b from-white/10 to-white/5 p-6">
                            <div class="text-xs tracking-[0.18em] uppercase font-semibold text-white/50">Quick Start</div>
                            <div class="mt-3 text-sm text-white/70 leading-relaxed">
                                <div class="font-semibold text-white">County Office Mode</div>
                                <div class="mt-2">Run on a laptop. Phones connect on the same Wi‑Fi.</div>
                                <div class="mt-3 rounded-2xl bg-black/30 border border-white/10 p-4 font-mono text-[12px] whitespace-pre-wrap">
cp .env.example .env
docker compose up -d --build
                                </div>
                                <div class="mt-3">Then open <span class="font-semibold text-white">/app</span> on phones and desktop.</div>
                            </div>
                        </div>
                        <div class="mt-4 rounded-3xl border border-white/10 bg-white/5 p-6">
                            <div class="text-xs tracking-[0.18em] uppercase font-semibold text-white/50">Admin</div>
                            <div class="mt-2 text-sm text-white/70">
                                Admin user is bootstrapped from environment on first deploy.
                                Email: <span class="font-semibold text-white">{{ env('ADMIN_EMAIL', 'geraldshikunyi@gmail.com') }}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="mt-14 text-xs text-white/45">
                    © {{ date('Y') }} MajiWatch Kenya. Built for Kenya’s mobile-first reality.
                </div>
            </div>
        </div>
    </body>
</html>

