from rest_framework import routers
from .views import FirstAidViewSet, HomeRemedyViewSet

router = routers.DefaultRouter()
router.register(r"first-aids", FirstAidViewSet, basename="first-aid")
router.register(r"home-remedies", HomeRemedyViewSet, basename="home-remedy")


urlpatterns = router.urls
