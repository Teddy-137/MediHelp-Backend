from django.http import JsonResponse
from django.db import connection, DatabaseError
from rest_framework.views import APIView


class HealthCheckView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        status_code = 200
        response = {
            "status": "ok",
            "services": {"database": "connected"},
            "version": "1.0.0",
        }

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1;")
        except DatabaseError:
            status_code = 503
            response.update(
                {
                    "status": "error",
                    "error": "Database connection failed",
                    "services": {"database": "unavailable"},
                }
            )

        return JsonResponse(response, status=status_code)
