"""CMV Traffic Alert report. Every panel is a read-only GET under /api/cmv-alerts/<panel>."""

from django.urls import path

from .views import DailyAlertsView

urlpatterns = [
    path("daily-alerts", DailyAlertsView.as_view(), name="cmv-daily-alerts"),
]
