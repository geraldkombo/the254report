# Laravel 13 Gateway Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Laravel 13 gateway that becomes the primary “front door” at `/` (public portal + login + admin), while keeping the existing FastAPI/Celery/PostGIS scoring engine and the existing React dashboard under `/app`.

**Architecture:** Keep current services (api/worker/beat/db/redis). Add a new `gateway` service (Laravel 13) for auth/roles/admin + public portal. Update the edge router (web) to route `/` → Laravel, `/app/*` → React SPA, `/api/*` + `/reports/*` → FastAPI.

**Tech Stack:** Laravel 13 (PHP 8.3), Postgres (shared), Redis (optional for sessions/queues), existing FastAPI (Python), existing React dashboard, Caddy edge router.

---

## File Structure

**Create**
- `gateway/` (Laravel 13 application root)
- `gateway/Dockerfile`
- `gateway/composer.json` (via Laravel scaffold)
- `gateway/routes/web.php`
- `gateway/app/Http/Middleware/RoleMiddleware.php`
- `gateway/app/Models/User.php` (role field)
- `gateway/database/migrations/*_add_role_to_users_table.php`
- `gateway/database/seeders/AdminUserSeeder.php`
- `gateway/resources/views/*` (Blade views: landing, login, admin)

**Modify**
- `docker-compose.yml` (add `gateway` service)
- `web/Caddyfile` (route `/` to gateway, `/app` to React, `/api` + `/reports` to api)
- `.env.example` (Laravel envs: APP_KEY, ADMIN_BOOTSTRAP_PASSWORD policy)
- `DEPLOYMENT.md` (gateway setup + first-login instructions)
- `README.md` (routing and URLs)

**Optional**
- `gateway/public/app/` (if embedding React build artifacts later)

---

## Task 1: Add Laravel 13 app skeleton under `gateway/`

**Files:**
- Create: `gateway/` (Laravel app)
- Create: `gateway/Dockerfile`
- Modify: `docker-compose.yml`

- [ ] **Step 1: Scaffold Laravel 13**

Run:
```bash
composer create-project laravel/laravel gateway
```
Expected: `gateway/artisan` exists.

- [ ] **Step 2: Add gateway Dockerfile**

Create `gateway/Dockerfile`:
```Dockerfile
FROM php:8.3-fpm-alpine

RUN apk add --no-cache bash git unzip icu-dev libzip-dev oniguruma-dev postgresql-dev \
  && docker-php-ext-install intl zip pdo pdo_pgsql

WORKDIR /var/www/html

COPY composer.json composer.lock ./
RUN php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');" \
  && php composer-setup.php --install-dir=/usr/local/bin --filename=composer \
  && rm composer-setup.php \
  && composer install --no-dev --no-interaction --prefer-dist --no-progress

COPY . .

RUN php artisan key:generate --force

CMD ["php-fpm"]
```

- [ ] **Step 3: Add gateway service to Compose**

Update `docker-compose.yml` to include:
- `gateway` (php-fpm)
- `gateway_web` (Caddy or nginx) that serves Laravel `public/` and proxies PHP to `gateway` fpm

Implementation guidance: use a dedicated Caddy container for Laravel routing (fastest, fewer moving parts).

- [ ] **Step 4: Add minimal Laravel web server**

Create `gateway/Caddyfile`:
```caddyfile
:8080
root * /var/www/html/public
php_fastcgi gateway:9000
file_server
encode zstd gzip
```

Add `gateway_web` container in compose:
- build `caddy:2-alpine`
- mount `gateway/` into `/var/www/html`
- use `gateway/Caddyfile`
- expose `8080` internally (no host port)

- [ ] **Step 5: Smoke test gateway container starts**

Run:
```bash
docker compose up -d --build gateway gateway_web
```
Expected: container healthy; `curl http://localhost:<edge>/` returns HTML once edge routing is connected in Task 4.

---

## Task 2: Add authentication (email/password) and roles (admin/regulator/county/public)

**Files:**
- Modify: `gateway/app/Models/User.php`
- Create: `gateway/app/Http/Middleware/RoleMiddleware.php`
- Modify: `gateway/routes/web.php`
- Create: `gateway/resources/views/auth/login.blade.php`
- Create: `gateway/app/Http/Controllers/Auth/LoginController.php`
- Create: `gateway/database/migrations/*_add_role_to_users_table.php`

- [ ] **Step 1: Add `role` column**

Migration:
```php
Schema::table('users', function (Blueprint $table) {
    $table->string('role')->default('public')->index();
});
```

- [ ] **Step 2: Implement login controller**

Use Laravel Auth:
- `POST /login` validates email/password and calls `Auth::attempt`.
- `POST /logout` calls `Auth::logout`.

- [ ] **Step 3: Add role middleware**

`RoleMiddleware` checks `auth()->user()->role` is in allowed list.

- [ ] **Step 4: Routes**

`routes/web.php`:
- `GET /` landing page (public portal links)
- `GET /login` + `POST /login`
- `POST /logout`
- `GET /admin` guarded by `role:admin`
- `GET /app` redirects to `/app/` (React)

---

## Task 3: Admin bootstrap (email is fixed, password is set at deploy time)

**Files:**
- Modify: `.env.example`
- Create: `gateway/database/seeders/AdminUserSeeder.php`
- Modify: `gateway/database/seeders/DatabaseSeeder.php`
- Modify: `DEPLOYMENT.md`

- [ ] **Step 1: Define env policy**

Add to `.env.example`:
- `ADMIN_EMAIL=geraldshikunyi@gmail.com`
- `ADMIN_BOOTSTRAP_PASSWORD=` (required for first deploy)

- [ ] **Step 2: Seeder creates admin if missing**

Seeder logic:
- Find user by `ADMIN_EMAIL`
- If missing, create with role `admin`
- If `ADMIN_BOOTSTRAP_PASSWORD` missing, abort with explicit error so deployment is never locked behind an unknown password

- [ ] **Step 3: Document first deploy**

In `DEPLOYMENT.md` add:
- set `ADMIN_BOOTSTRAP_PASSWORD` on first deploy
- login, then rotate password and remove bootstrap password from `.env`

---

## Task 4: Edge routing (single origin)

**Files:**
- Modify: `web/Caddyfile`

- [ ] **Step 1: Route table**

Update `web/Caddyfile`:
- `/api/*` → `api:8000`
- `/reports/*` → `api:8000`
- `/app/*` → serve React SPA static
- everything else → `reverse_proxy gateway_web:8080`

- [ ] **Step 2: Verify same-origin**

Expected:
- `GET /` renders Laravel landing
- `GET /app/` renders React dashboard
- React calls `/api/...` (already configured)

---

## Task 5: Production hardening checklist

**Files:**
- Modify: `DEPLOYMENT.md`
- Modify: `security_best_practices_report.md`

- [ ] **Step 1: Cookies/session**
- [ ] **Step 2: CSRF**
- [ ] **Step 3: Rate limiting at edge**
- [ ] **Step 4: Disable debug in production**

---

## Self-Review
- Spec coverage: gateway at `/`, admin-first for admins, public portal, dashboard at `/app`, API at `/api`, stable deploy and password policy.
- Placeholder scan: no TBD/TODO remains in tasks.
- Type consistency: env names and routes consistent across tasks.

---

## Execution Handoff
Plan complete and saved to `docs/superpowers/plans/2026-05-01-laravel-13-gateway.md`. Two execution options:
1) Subagent-Driven (recommended)
2) Inline Execution

