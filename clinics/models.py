from django.contrib.gis.db import models


class Clinic(models.Model):
    name = models.CharField(max_length=200)
    location = models.PointField(geography=True, null=True)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    opening_hours = models.JSONField(default=dict)

    def __str__(self):
        return self.name
