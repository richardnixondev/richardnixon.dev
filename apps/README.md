# Django Apps

## accounts

Custom user model with email-based authentication (no username). Roles: `owner` and `registered`. Extends `AbstractBaseUser` + `PermissionsMixin`. Used by django-allauth for Google/GitHub OAuth and django-two-factor-auth for 2FA/OTP.

## api

REST API powered by django-ninja. Exposes endpoints for blog posts, portfolio projects, contact form, and homepage data. Consumed by the Next.js frontend (`frontend/`).

## blog

Blog engine with posts, tags, and categories. Features:
- Markdown rendering with Pygments syntax highlighting
- CKEditor 5 rich text editor in admin
- RSS feed (`/feed/`)
- SEO sitemap (`sitemaps.py`)
- i18n support via django-modeltranslation

## contact

Contact form with model-backed storage and reCAPTCHA v3 validation. Includes a resume download view.

## core

Lightweight utility app. Contains the `/health/` endpoint for Docker healthchecks and monitoring.

## portfolio

Projects showcase with technologies/tags. Features:
- SEO sitemap (`sitemaps.py`)
- i18n support via django-modeltranslation
- Related projects
