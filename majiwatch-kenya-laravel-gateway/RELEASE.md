# Release Checklist

## Pre-release
- Update `.env.example` defaults (do not commit real secrets)
- Run backend compile: `python -m compileall server/app`
- Run frontend build:
  - `cd web && npm ci && npm run build`
- Validate API endpoints:
  - `./scripts/test.sh` (set `API_KEY` env first)
- Build ZIP:
  - `./scripts/make_zip.sh majiwatch-kenya.zip`

## Release assets
- Attach `majiwatch-kenya.zip`
- Attach press kit folder (`presskit/`)

## Suggested release notes template
- What’s new
- Breaking changes
- Deployment notes
- Security notes (secret rotation, CORS allowlist)

