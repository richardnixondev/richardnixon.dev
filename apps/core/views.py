import logging

from django.db import connection
from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.cache import never_cache

logger = logging.getLogger(__name__)


@never_cache
def health(request):
    db_ok = False
    cache_ok = False

    try:
        connection.ensure_connection()
        db_ok = True
    except Exception:
        logger.warning("Health check: database connection failed")

    try:
        cache.set("_health_check", "1", timeout=5)
        cache_ok = cache.get("_health_check") == "1"
    except Exception:
        logger.warning("Health check: cache connection failed")

    status_code = 200 if (db_ok and cache_ok) else 503
    return JsonResponse(
        {"status": "ok" if status_code == 200 else "degraded", "db": db_ok, "cache": cache_ok},
        status=status_code,
    )
