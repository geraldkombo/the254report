# Security Best Practices Report — MajiWatch Kenya (1 May 2026)

## Executive Summary
The codebase is generally safe-by-default for a local deployment and already avoids committing secrets. This report focuses on production-hardening gaps: CORS defaults, proxying to keep same-origin, basic secret hygiene, and operational recommendations.

## Critical

### C1. Public CORS wildcard in earlier build
- **Impact**: When deployed on the public internet, permissive CORS can enable unauthorized cross-site reads of API responses and weakens browser-side trust boundaries.
- **Fix**: Replaced wildcard CORS with an allowlist via `CORS_ALLOW_ORIGINS` and restricted methods/headers.
- Code: [main.py:L13-L28](file:///workspace/server/app/main.py#L13-L28), [.env.example:L1-L20](file:///workspace/.env.example#L1-L20)

## High

### H1. API should be served behind same-origin proxy for mobile caching and reduced attack surface
- **Risk**: Mixed origins (web on :3000 and API on :8000) complicate PWA caching and increase exposure for CORS misconfiguration.
- **Fix**: Added web reverse-proxy paths `/api/*` and `/reports/*` for the Docker deployment.
- Code: [Caddyfile](file:///workspace/web/Caddyfile), [api.ts](file:///workspace/web/src/lib/api.ts)

### H2. Secrets must never be committed; default placeholders must be rotated
- **Risk**: Users may deploy with `change-me` defaults.
- **Mitigation**: `.env.example` documents required secrets (`API_KEY_CHANGE_ME`, `ORACLE_SIGNING_SECRET`) and warns to rotate.
- Code: [.env.example](file:///workspace/.env.example)

## Medium

### M1. Browser-stored operator key
- **Risk**: LocalStorage API keys can be copied by anyone with access to the device/browser profile.
- **Mitigation**: Intended for operator/admin use only; recommend deploying on trusted devices, and rotating keys if device is lost. Prefer server-side auth for multi-user deployments.
- Code: [settings.ts](file:///workspace/web/src/lib/settings.ts)

### M2. Rate limiting not implemented
- **Risk**: Public deployments can be scraped or abused.
- **Recommendation**: Add an edge reverse proxy (Caddy/NGINX) rate limit policy for `/api/*` and consider per-key throttling.

## Operational Recommendations
- Serve via HTTPS for public internet deployments (reverse proxy termination).
- Keep Postgres and Redis private (no public ports).
- Back up `db_data` volume; rotate secrets on incident.

