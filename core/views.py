# apps/core/views.py
import platform
import os

from django.conf import settings
from django.db import connection
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema


@extend_schema(
    summary="Service health check",
    description="""
    Returns the status of critical subsystems:
    - **database**: can execute a simple query  
    - **cache**: can set/get a cache key  
    - **ai_api**: has a configured API key  
    """,
    responses={
        200: {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "version": {"type": "string"},
                "environment": {"type": "string"},
                "services": {
                    "type": "object",
                    "properties": {
                        "database": {"type": "string"},
                        "cache": {"type": "string"},
                        "ai_api": {"type": "string"},
                    },
                },
                "system": {
                    "type": "object",
                    "properties": {
                        "django": {"type": "string"},
                        "python": {"type": "string"},
                    },
                },
            },
        }
    },
)
class HealthCheckView(APIView):
    permission_classes = []
    authentication_classes = []
    throttle_classes = []

    def get(self, request):

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1;")
                _ = cursor.fetchone()
            db_status = "connected"
        except Exception:
            db_status = "unavailable"

        try:
            cache.set("healthcheck_ping", "pong", timeout=5)
            val = cache.get("healthcheck_ping")
            cache_status = "connected" if val == "pong" else "degraded"
        except Exception:
            cache_status = "unavailable"

        ai_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        ai_status = "configured" if ai_key else "missing"

        payload = {
            "status": "ok",
            "version": getattr(settings, "APP_VERSION", "1.0.0"),
            "environment": getattr(settings, "ENVIRONMENT", "development"),
            "services": {
                "database": db_status,
                "cache": cache_status,
                "ai_api": ai_status,
            },
            "system": {
                "django": (
                    settings.DJANGO_VERSION
                    if hasattr(settings, "DJANGO_VERSION")
                    else platform.python_version()
                ),
                "python": platform.python_version(),
            },
        }

        http_status = (
            status.HTTP_200_OK
            if db_status == "connected"
            else status.HTTP_503_SERVICE_UNAVAILABLE
        )
        return Response(payload, status=http_status)
