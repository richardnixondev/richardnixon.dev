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
- `FORGEJO_DB_PASSWORD`, `FORGEJO_SECRET_KEY`, `FORGEJO_INTERNAL_TOKEN`, `FORGEJO_OAUTH2_JWT_SECRET` — see Forgejo section below for generation commands

## 4. Start core services

```bash
cd infrastructure
docker compose up -d
```

This starts all services: Traefik, PostgreSQL, Redis, Django, Celery, WordPress, Umami, Grafana, Prometheus, LocFlow, EireScope, Authentik, Forgejo.

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
| Forgejo | 3000 (HTTP), 2222 (SSH on host) | git.richardnixon.dev |

## Forgejo (git.richardnixon.dev)

Self-hosted Git forge with public repository browsing and SSO via Authentik.

### Generate secrets

```bash
echo "FORGEJO_DB_PASSWORD=$(openssl rand -base64 24 | tr -d '/+=' | head -c 32)"
echo "FORGEJO_SECRET_KEY=$(openssl rand -base64 48 | tr -d '\n')"
echo "FORGEJO_INTERNAL_TOKEN=$(openssl rand -base64 64 | tr -d '\n')"
echo "FORGEJO_OAUTH2_JWT_SECRET=$(openssl rand -base64 32 | tr -d '=' | tr '+/' '-_')"
```

Paste the output into `infrastructure/.env`.

### Bootstrap the admin user

Registration is disabled (`DISABLE_REGISTRATION=true`), so create the first admin via the CLI:

```bash
docker compose exec -u git forgejo forgejo admin user create \
  --username <yourname> --email <you@example.com> --admin \
  --password "$(openssl rand -base64 18)" --must-change-password=false
```

(`admin` is a reserved name in Forgejo — use a different username.)

### SSH cloning

Forgejo SSH listens on host port **2222** (port 22 is used by the host's sshd). Clone URL format:

```
ssh://git@git.richardnixon.dev:2222/<user>/<repo>.git
```

### Wiring up Authentik SSO (OIDC)

1. In Authentik admin (`auth.richardnixon.dev`), create an **OAuth2/OpenID Provider** with redirect URI `https://git.richardnixon.dev/user/oauth2/Authentik/callback` (the `Authentik` segment is the source name in step 4 — case-sensitive).
2. Create an **Application** bound to that provider with slug `forgejo`.
3. Copy the Client ID and Client Secret into `.env` as `FORGEJO_OIDC_CLIENT_ID` / `FORGEJO_OIDC_CLIENT_SECRET`.
4. Register the source in Forgejo via CLI:

   ```bash
   docker compose exec -u git forgejo forgejo admin auth add-oauth \
     --name Authentik \
     --provider openidConnect \
     --key "$FORGEJO_OIDC_CLIENT_ID" \
     --secret "$FORGEJO_OIDC_CLIENT_SECRET" \
     --auto-discover-url "https://auth.richardnixon.dev/application/o/forgejo/.well-known/openid-configuration" \
     --scopes "openid profile email"
   ```

The compose already sets `oauth2_client.ENABLE_AUTO_REGISTRATION=true` and `ACCOUNT_LINKING=auto`, so existing accounts whose email matches the Authentik user are linked automatically, and new Authentik users get a Forgejo account on first login.

Provisioning the provider via the Authentik shell (alternative to the admin UI):

```bash
docker compose exec authentik-server ak shell -c '
from authentik.flows.models import Flow
from authentik.providers.oauth2.models import OAuth2Provider, ClientTypes, IssuerMode, ScopeMapping, RedirectURI, RedirectURIMatchingMode
from authentik.core.models import Application
from authentik.crypto.models import CertificateKeyPair

flow = Flow.objects.get(slug="default-provider-authorization-implicit-consent")
key = CertificateKeyPair.objects.exclude(key_data="").first()
scopes = ScopeMapping.objects.filter(managed__in=[
    "goauthentik.io/providers/oauth2/scope-openid",
    "goauthentik.io/providers/oauth2/scope-email",
    "goauthentik.io/providers/oauth2/scope-profile",
])
p, _ = OAuth2Provider.objects.update_or_create(name="Forgejo", defaults=dict(
    client_type=ClientTypes.CONFIDENTIAL, authorization_flow=flow, signing_key=key,
    issuer_mode=IssuerMode.PER_PROVIDER))
p.redirect_uris = [RedirectURI(matching_mode=RedirectURIMatchingMode.STRICT,
    url="https://git.richardnixon.dev/user/oauth2/Authentik/callback")]
p.save()
p.property_mappings.set(scopes)
Application.objects.update_or_create(slug="forgejo", defaults=dict(
    name="Forgejo", provider=p, meta_launch_url="https://git.richardnixon.dev/"))
print("CLIENT_ID=" + p.client_id); print("CLIENT_SECRET=" + p.client_secret)
'
```

### Observability

Forgejo metrics are exposed unauthenticated on the `monitoring` network at `forgejo:3000/metrics` and scraped automatically by Prometheus (job `forgejo`). Logs flow into Loki via Promtail like every other container.
