from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from core.views import HealthView, MeView

urlpatterns = [
    path("api/health", HealthView.as_view(), name="health"),
    path("api/me", MeView.as_view(), name="me"),
    path("api/cmv-alerts/", include("cmv_alerts.urls")),
    path("api/schema", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
]
