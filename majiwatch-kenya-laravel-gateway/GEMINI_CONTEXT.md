# Gemini Pro Context Pack (Copy/Paste)

If you want to work on this repo with Gemini Pro, the most reliable way is to paste:
1) this file, then
2) `README.md`, `DEPLOYMENT.md`, and
3) the core code paths below.

## Repo purpose (one paragraph)
MajiWatch Kenya is an open-source, mobile-first water & sanitation intelligence platform for Kenya (47 counties). It ingests public sources, computes nightly county scores (0–100), triggers watch/warning/emergency alerts, generates emergency PDF briefs, and exposes a REST API plus a map-first dashboard.

## Core code paths
- Backend entrypoint: `server/app/main.py`
- API routes: `server/app/api/router.py`
- DB models: `server/app/db/models.py`
- Bootstrap/seed: `server/app/bootstrap.py`
- ETL baseline + ingestion artifacts: `server/app/etl/ingest.py`, `server/app/etl/ingest_all.py`
- Scoring: `server/app/scoring/compute.py`
- Alerts + PDF: `server/app/alerts/logic.py`, `server/app/reporting/emergency_report.py`
- Celery jobs: `server/app/tasks/jobs.py`, `server/app/tasks/celery_app.py`
- Frontend map + navigation: `web/src/components/CountyMap.tsx`, `web/src/components/AppShell.tsx`
- Frontend API client: `web/src/lib/api.ts`

## “May 2026 mobile-first” constraints
- Low bandwidth + intermittent connectivity
- Viewport-based loading for water points via vector tiles (`/api/tiles/waterpoints/...`)
- Offline fallback map style (`web/public/styles/offline.json`)

## Security constraints
- Never hardcode secrets; use `.env` (not committed)
- Protected endpoints require `X-API-Key`
- Signed oracle endpoint requires `ORACLE_SIGNING_SECRET`

