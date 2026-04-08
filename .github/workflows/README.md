# CI/CD Workflows

## deploy.yml

Two-stage pipeline triggered on pushes and PRs to `main`.

### Job 1 — ci

Runs on every push and PR:

- Installs Python 3.12 + project dependencies
- Spins up PostgreSQL 16 and Redis 7 as service containers
- Runs `python manage.py check --deploy` (Django deployment checks)
- Runs `pytest apps/ --tb=short -q` (test suite)
- Validates `infrastructure/docker-compose.yml` syntax

### Job 2 — deploy

Runs only on push to `main`, after `ci` passes:

- SSHs into the VPS
- Pulls latest code, rebuilds containers, runs migrations
- Smoke-tests `https://richardnixon.dev/health/`

## Required GitHub Secrets

| Secret             | Description                                      |
|--------------------|--------------------------------------------------|
| `VPS_HOST`         | VPS IP address or hostname                       |
| `VPS_USER`         | SSH username (e.g. `root`)                       |
| `VPS_SSH_KEY`      | Private SSH key for VPS access                   |
| `DJANGO_SECRET_KEY`| Django secret key used in CI `check --deploy`    |

### Setting secrets

1. Go to **Settings > Secrets and variables > Actions** in the GitHub repo
2. Click **New repository secret** for each secret above
3. For `VPS_SSH_KEY`, paste the full private key including `-----BEGIN/END-----` lines
