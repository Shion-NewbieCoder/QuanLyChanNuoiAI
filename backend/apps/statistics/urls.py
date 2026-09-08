from django.urls import path

from .views import CostStatisticsView, GrowthStatisticsView, MortalityStatisticsView


urlpatterns = [
    path("statistics/growth", GrowthStatisticsView.as_view(), name="statistics-growth"),
    path("statistics/costs", CostStatisticsView.as_view(), name="statistics-costs"),
    path("statistics/mortality", MortalityStatisticsView.as_view(), name="statistics-mortality"),
]
