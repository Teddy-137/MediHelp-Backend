from django.contrib.gis.geos import Point
from django.test import TestCase
from .models import Clinic


class ClinicTests(TestCase):
    def test_nearby_query(self):
        clinic = Clinic.objects.create(
            name="Test Clinic", location=Point(38.7636, 9.0054), phone="+251123456789"
        )
        response = self.client.get("/clinics/nearby/?lat=9.005&lng=38.763")
        self.assertContains(response, "Test Clinic")
