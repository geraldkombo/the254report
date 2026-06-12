# Contributing to MAJI Sentinel

## Quick Development Setup
Prerequisites:
- Docker + Docker Compose
- Node.js (for local frontend dev)

Steps:
```bash
cp .env.example .env
docker compose up -d --build
```

Frontend dev:
```bash
cd web
npm install
npm run dev -- --host 0.0.0.0 --port 3000
```

Backend dev (without Docker) is supported, but the recommended path is via Docker Compose because PostGIS and Redis are required.

## Project Structure
- `server/`: FastAPI API + Celery tasks (shared image for api/worker/beat)
- `web/`: React dashboard (MapLibre)
- `db/`: database initialization scripts
- `scripts/`: test utilities

## Pull Request Guidelines
- Keep PRs focused and small when possible.
- Add/adjust API endpoints via `server/app/api/router.py`.
- Avoid logging secrets; never commit `.env`.
- If you change scoring logic, update `README.md` and keep formulas explicit.
- Run `npm run build` in `web/` before opening a PR.

## Reporting Issues
Please include:
- Steps to reproduce
- Expected vs actual behavior
- Logs (redact secrets)
- OS + Docker version

