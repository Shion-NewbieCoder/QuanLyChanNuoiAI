from datetime import date

from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.users.permissions import RoleActionPermission

from .services import get_cost_statistics, get_growth_statistics, get_loss_statistics


class StatisticsBaseView(APIView):
    permission_classes = [IsAuthenticated, RoleActionPermission]
    permission_resource = "statistics"

    def get_date_filters(self, request):
        values = {}
        for parameter in ("start_date", "end_date"):
            raw_value = request.query_params.get(parameter)
            if raw_value:
                try:
                    values[parameter] = date.fromisoformat(raw_value)
                except ValueError:
                    return None, Response(
                        {parameter: "Use YYYY-MM-DD."},
                        status=400,
                    )
        if (
            values.get("start_date")
            and values.get("end_date")
            and values["end_date"] < values["start_date"]
        ):
            return None, Response(
                {"end_date": "end_date must be on or after start_date."},
                status=400,
            )
        return values, None


class GrowthStatisticsView(StatisticsBaseView):
    def get(self, request):
        return Response(get_growth_statistics())


class CostStatisticsView(StatisticsBaseView):
    def get(self, request):
        filters, error = self.get_date_filters(request)
        if error:
            return error
        return Response(get_cost_statistics(**filters))


class MortalityStatisticsView(StatisticsBaseView):
    def get(self, request):
        filters, error = self.get_date_filters(request)
        if error:
            return error
        return Response(get_loss_statistics(**filters))
