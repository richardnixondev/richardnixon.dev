# Deployment Guide

Step-by-step guide to deploy richardnixon.dev on a fresh VPS.

## Prerequisites

- Ubuntu 22.04+ VPS with root access
- Domain DNS pointing to VPS IP (A records for `richardnixon.dev`, `*.richardnixon.dev`)
- Docker Engine 24+ and Docker Compose v2

## 1. Install Docker

```bash
curl -fsSL https://get.docker.com | sh
```

## 2. Clone the repository

```bash
cd /root
git clone git@github.com:richardnixondev/richardnixon.dev.git
cd richardnixon.dev
```

## 3. Configure environment

```bash
cp infrastructure/.env.example infrastructure/.env
```

Edit `infrastructure/.env` and fill in all required values. At minimum:

- `DJANGO_SECRET_KEY` — generate with:
  ```bash
  python3 -c "from secrets import token_urlsafe; print(token_urlsafe(50))"
  ```
- `PLATFORM_DB_PASSWORD`, `LOCFLOW_DB_PASSWORD`, `UMAMI_DB_PASSWORD` — strong random passwords
- `MYSQL_ROOT_PASSWORD`, `WP_DB_PASSWORD` — for WordPress
- `GRAFANA_ADMIN_PASSWORD`
- `CROWDSEC_BOUNCER_KEY` — generated after first CrowdSec startup (see step 6)
- `AUTHENTIK_SECRET_KEY`, `AUTHENTIK_DB_PASSWORD`

## 4. Start core services

```bash
cd infrastructure
docker compose up -d
```

This starts all services: Traefik, PostgreSQL, Redis, Django, Celery, WordPress, Umami, Grafana, Prometheus, LocFlow, EireScope, Authentik.

Traefik automatically provisions Let's Encrypt SSL certificates.

## 5. Run initial migrations and create superuser

```bash
docker compose exec platform-web python manage.py migrate
docker compose exec platform-web python manage.py createsuperuser
docker compose exec platform-web python manage.py collectstatic --no-input
```

## 6. Configure CrowdSec bouncer

```bash
docker compose exec crowdsec cscli bouncers add traefik-bouncer
```

Copy the generated key into `infrastructure/.env` as `CROWDSEC_BOUNCER_KEY`, then restart:

```bash
docker compose restart crowdsec-bouncer
```

## 7. Verify deployment

```bash
# Check all containers are healthy
docker compose ps

# Smoke test
curl https://richardnixon.dev/health/
# Expected: {"status": "ok", "db": true, "cache": true}
```

## 8. Configure OAuth (optional)

1. Go to `https://richardnixon.dev/admin/`
2. Under **Social applications**, add Google and/or GitHub OAuth providers
3. Get credentials from Google Cloud Console / GitHub Developer Settings

## 9. Set up GitHub Actions CI/CD (optional)

Add the following secrets to the GitHub repository (Settings > Secrets > Actions):

| Secret | Value |
|--------|-------|
| `VPS_HOST` | VPS IP address |
| `VPS_USER` | `root` |
| `VPS_SSH_KEY` | SSH private key |
| `DJANGO_SECRET_KEY` | Same as in `.env` |

After this, every push to `main` will automatically deploy.

## Updating

Manual update:

```bash
cd /root/richardnixon.dev
git pull origin main
docker compose -f infrastructure/docker-compose.yml build platform-web locflow-web eirescope
docker compose -f infrastructure/docker-compose.yml up -d
docker compose -f infrastructure/docker-compose.yml exec -T platform-web python manage.py migrate --no-input
docker compose -f infrastructure/docker-compose.yml exec -T platform-web python manage.py collectstatic --no-input
```

## Services and ports

All services are behind Traefik (ports 80/443). No service exposes ports directly to the internet.

| Service | Internal port | URL |
|---------|--------------|-----|
| Django platform | 8000 | richardnixon.dev |
| Next.js frontend | 3000 | richardnixon.dev (via Traefik routing) |
| LocFlow API | 8000 | locflow.richardnixon.dev |
| EireScope | 5000 | osint.richardnixon.dev |
| WordPress | 80 | richardemanu.com |
| Umami | 3000 | analytics.richardnixon.dev |
| Grafana | 3000 | status.richardnixon.dev |
| Portainer | 9443 | portainer.richardnixon.dev |
| Authentik | 9000 | auth.richardnixon.dev |
