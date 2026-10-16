from django.urls import path

from .views import ChatView, GrowthReportView, HerdSummaryView, ReminderView


urlpatterns = [
    path("chat", ChatView.as_view(), name="ai-chat"),
    path("reminders", ReminderView.as_view(), name="ai-reminders"),
    path("herd-summary", HerdSummaryView.as_view(), name="ai-herd-summary"),
    path("growth-report", GrowthReportView.as_view(), name="ai-growth-report"),
]
