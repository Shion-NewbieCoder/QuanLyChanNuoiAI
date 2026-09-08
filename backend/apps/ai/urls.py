from django.urls import path

from .views import GrowthReportView, HerdSummaryView, ReminderView


urlpatterns = [
    path("reminders", ReminderView.as_view(), name="ai-reminders"),
    path("herd-summary", HerdSummaryView.as_view(), name="ai-herd-summary"),
    path("growth-report", GrowthReportView.as_view(), name="ai-growth-report"),
]
