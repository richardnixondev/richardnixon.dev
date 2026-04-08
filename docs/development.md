# Local Development Guide

## Prerequisites

- Python 3.12+
- PostgreSQL 16 and Redis 7 (or Docker for services only)
- Node.js 22+ (for the frontend)

## Option A: Docker Compose (recommended)

Use Docker Compose for databases, run Django directly.

### 1. Start services

```bash
docker compose -f infrastructure/docker-compose.yml up -d platform-db platform-redis
```

### 2. Set up Python environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.txt
```

### 3. Configure environment

```bash
export DJANGO_SETTINGS_MODULE=config.settings.development
export POSTGRES_DB=platform
export POSTGRES_USER=platform
export POSTGRES_PASSWORD=platform
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export REDIS_URL=redis://localhost:6379/0
export CELERY_BROKER_URL=redis://localhost:6379/1
```

Or create a `.env` file and use `python-dotenv`.

### 4. Run migrations and start server

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit http://localhost:8000/

### 5. Run Celery (optional)

In a separate terminal:

```bash
celery -A config worker -l info
celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

## Option B: Full Docker stack

Run everything in Docker (mirrors production):

```bash
cp infrastructure/.env.example infrastructure/.env
# Edit .env with local values

docker compose -f infrastructure/docker-compose.yml up -d platform-db platform-redis platform-web
```

## Frontend development

The Next.js frontend lives in `frontend/`.

```bash
cd frontend
npm install
npm run dev
```

Visit http://localhost:3000/

The frontend proxies API calls to the Django backend. Set `API_URL=http://localhost:8000/api` if the backend runs on a different port.

## Running tests

```bash
# All tests
pytest apps/ -v

# With coverage
pytest apps/ --cov=apps --cov-report=term-missing

# Single app
pytest apps/accounts/ -v
```

## Linting

```bash
ruff check .
ruff format --check .
mypy apps/
```

## Useful commands

```bash
# Create new migrations
python manage.py makemigrations

# Compile translations
python manage.py compilemessages

# Collect static files
python manage.py collectstatic

# Django shell
python manage.py shell

# Check for issues
python manage.py check
```
