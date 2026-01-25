# richardnixon.dev

Personal portfolio and blog platform built with Django, deployed with Docker.

## Architecture

```
                                    ┌─────────────────┐
                                    │   Cloudflare    │
                                    │      DNS        │
                                    └────────┬────────┘
                                             │
                                    ┌────────▼────────┐
                                    │    Traefik      │
                                    │  (Reverse Proxy)│
                                    │   + SSL/TLS     │
                                    └────────┬────────┘
                                             │
              ┌──────────────────────────────┼──────────────────────────────┐
              │                              │                              │
     ┌────────▼────────┐           ┌────────▼────────┐           ┌────────▼────────┐
     │  Django Platform │           │    WordPress    │           │     Umami       │
     │ richardnixon.dev │           │ richardemanu.com│           │    Analytics    │
     └────────┬────────┘           └─────────────────┘           └─────────────────┘
              │
    ┌─────────┼─────────┐
    │         │         │
┌───▼───┐ ┌───▼───┐ ┌───▼───┐
│Postgres│ │ Redis │ │Celery │
└───────┘ └───────┘ └───────┘
```

## Services

| Service | Domain | Description |
|---------|--------|-------------|
| Django Platform | richardnixon.dev | Blog, portfolio, contact |
| WordPress | richardemanu.com | Personal site |
| Umami | analytics.richardnixon.dev | Privacy-focused analytics |
| Grafana | status.richardnixon.dev | Observability dashboards |
| Portainer | portainer.richardnixon.dev | Docker management |

## Technology Stack

### Application
- **Backend**: Django 5.x, Celery, PostgreSQL 16, Redis 7
- **Frontend**: Django Templates, HTMX, TailwindCSS
- **Auth**: django-allauth (Google/GitHub OAuth), django-two-factor-auth (2FA)
- **i18n**: English + Portuguese (django-modeltranslation)

### Infrastructure
- **Reverse Proxy**: Traefik v3.3 with Let's Encrypt SSL
- **Containers**: Docker Compose
- **Monitoring**: Prometheus, Grafana, Loki, Promtail, cAdvisor

### Security
- **CrowdSec**: IPS with community threat intelligence
- **Fail2ban**: SSH brute-force protection
- **GeoIP Blocking**: SSH restricted to Ireland only
- **reCAPTCHA v3**: Contact form spam protection

## Project Structure

```
richardnixon.dev/
├── apps/
│   ├── accounts/       # Custom user model (email-based)
│   ├── blog/           # Blog posts, Markdown, RSS
│   ├── portfolio/      # Projects showcase
│   └── contact/        # Contact form with reCAPTCHA
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── celery.py
│   └── wsgi.py
├── templates/
├── static/
├── locale/             # i18n translations
├── docker/
│   ├── Dockerfile
│   └── Dockerfile.full
└── infrastructure/     # Docker Compose configs
    ├── docker-compose.yml
    ├── .env.example
    ├── traefik/
    ├── prometheus/
    ├── loki/
    ├── promtail/
    ├── grafana/
    └── crowdsec/
```

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Domain with DNS configured

### Deployment

1. Clone the repository:
```bash
git clone https://github.com/richardnixondev/richardnixon.dev.git
cd richardnixon.dev/infrastructure
```

2. Create environment file:
```bash
cp .env.example .env
# Edit .env with your credentials
```

3. Start services:
```bash
docker compose up -d
```

4. Run migrations:
```bash
docker compose exec platform-web python manage.py migrate
docker compose exec platform-web python manage.py createsuperuser
```

## Environment Variables

See `infrastructure/.env.example` for all required variables:

| Variable | Description |
|----------|-------------|
| `DJANGO_SECRET_KEY` | Django secret key |
| `PLATFORM_DB_PASSWORD` | PostgreSQL password |
| `DJANGO_SUPERUSER_EMAIL` | Admin email (optional) |
| `RECAPTCHA_PUBLIC_KEY` | reCAPTCHA v3 site key |
| `RECAPTCHA_PRIVATE_KEY` | reCAPTCHA v3 secret key |
| `GRAFANA_ADMIN_PASSWORD` | Grafana admin password |
| `CROWDSEC_BOUNCER_KEY` | CrowdSec bouncer API key |

## Security Configuration

### CrowdSec

Installed collections:
- `crowdsecurity/traefik` - Web attack detection
- `crowdsecurity/http-cve` - CVE exploit detection
- `crowdsecurity/linux` - Linux system protection
- `crowdsecurity/whitelist-good-actors` - CDN/bot whitelist

Country blocks (web traffic):
- Russia (RU)
- China (CN)
- North Korea (KP)
- Iran (IR)
- Ukraine (UA)

Useful commands:
```bash
# View metrics
docker exec crowdsec cscli metrics

# List active bans
docker exec crowdsec cscli decisions list

# Add manual ban
docker exec crowdsec cscli decisions add --ip 1.2.3.4 --duration 24h --reason "manual"

# View alerts
docker exec crowdsec cscli alerts list
```

### SSH Security

| Protection | Configuration |
|------------|---------------|
| Fail2ban | 3 attempts = 24h ban |
| GeoIP | Only Ireland (IE) allowed |
| CrowdSec | SSH brute-force detection |

### Firewall Rules

SSH access is restricted by GeoIP to Ireland only:
```bash
# View current rules
iptables -L INPUT -n

# Rules persist in /etc/iptables/rules.v4
```

## Monitoring

### Grafana Dashboards

Access: https://status.richardnixon.dev

Available dashboards:
- **Docker Containers**: CPU, memory, network metrics
- **Container Logs**: Real-time log viewer with search

### Prometheus Metrics

Metrics collected by cAdvisor:
- Container CPU usage
- Container memory usage
- Network I/O
- Disk I/O

### Log Aggregation

Loki + Promtail collect logs from:
- All Docker containers
- System logs (/var/log)

## Common Commands

### Docker Management
```bash
# Start all services
docker compose up -d

# View container status
docker compose ps

# View logs
docker compose logs -f platform-web
docker compose logs -f platform-celery

# Rebuild after code changes
docker compose build platform-web platform-celery platform-celery-beat
docker compose up -d platform-web platform-celery platform-celery-beat
```

### Django Management
```bash
docker compose exec platform-web python manage.py migrate
docker compose exec platform-web python manage.py makemigrations
docker compose exec platform-web python manage.py createsuperuser
docker compose exec platform-web python manage.py collectstatic
docker compose exec platform-web python manage.py shell
```

### Security Management
```bash
# Check fail2ban status
fail2ban-client status sshd

# View CrowdSec decisions
docker exec crowdsec cscli decisions list

# View iptables rules
iptables -L INPUT -n -v
```

## URL Routes

| Path | Description |
|------|-------------|
| `/` | Blog home |
| `/admin/` | Django admin (2FA enabled) |
| `/accounts/` | Authentication (OAuth) |
| `/portfolio/` | Projects showcase |
| `/contact/` | Contact form (reCAPTCHA) |
| `/sitemap.xml` | XML sitemap |
| `/feed/` | RSS feed |

## License

MIT License
