# Deployment Guide (May 2026)

This guide covers the most stable deployment patterns for Kenya’s mobile-first reality: LAN-first (county office), plus optional public internet hosting.

## 1) Recommended: County Office “LAN Mode” (phones on same Wi‑Fi)
### Why this is the most stable
- Works even with unreliable internet
- Phones connect via local network
- No cloud costs

### Steps
1. Install Docker Desktop (Windows/macOS) or Docker Engine (Linux).
2. Clone or unzip this repo on the host machine.
3. Configure:
   - `cp .env.example .env`
   - Set `API_KEY_CHANGE_ME` and `ORACLE_SIGNING_SECRET` to strong values
4. Start:
   - `docker compose up -d --build`
5. Open:
   - Portal: `http://localhost:3000/`
   - Dashboard: `http://localhost:3000/app/`
   - Admin: `http://localhost:3000/admin`
   - API docs: `http://localhost:3000/api/docs`
6. Phone access (same Wi‑Fi):
   - Find host IP (e.g., `192.168.0.10`)
   - Open `http://192.168.0.10:3000/app/`
   - Add to Home Screen (PWA)

Notes:
- The dashboard calls the API via `/api/...` behind the web server proxy.
- Emergency PDFs are served under `/reports/...` from the same origin as the dashboard.
- The Laravel gateway bootstraps admin credentials on first run (see below).

## Admin first-login (no password required upfront)
Admin email is configured in `.env`:
- `ADMIN_EMAIL=geraldshikunyi@gmail.com`

On first deploy, if `ADMIN_BOOTSTRAP_PASSWORD` is empty, the gateway generates a strong random password and stores it in a private container volume.

Get the generated password:
```bash
docker compose exec gateway sh -lc 'cat /state/admin_password'
```

Then login at:
- `http://localhost:3000/login`

After you set a new password in the UI, you can delete the stored bootstrap password:
```bash
docker compose exec gateway sh -lc 'rm -f /state/admin_password'
```

## 2) Public Internet “Server Mode” (HTTPS)
### Target architecture
- A small VPS runs Docker Compose
- A reverse proxy provides HTTPS (Caddy/NGINX/Traefik)
- Dashboard and API are served under one origin (best for PWA caching)

### Steps (high level)
1. Provision a VPS (2 vCPU, 4–8 GB RAM recommended).
2. Install Docker + Docker Compose.
3. Set firewall:
   - allow 80/443 inbound
   - restrict 5432/6379 to localhost only
4. Configure `.env`:
   - `PUBLIC_BASE_URL=https://<your-domain>`
   - `CORS_ALLOW_ORIGINS=https://<your-domain>`
5. Start:
   - `docker compose up -d --build`
6. Add HTTPS (choose one):
   - Put Caddy/Traefik in front of `web` and terminate TLS

## 3) Operations Checklist
- Backups: snapshot Postgres volume `db_data` regularly
- Secrets: never commit `.env`; rotate `API_KEY_CHANGE_ME` if leaked
- Monitoring: review `/data/downloads` artifacts and ingestion run status in DB
- Updates: rebuild images; validate `web` builds and API health before rollout
