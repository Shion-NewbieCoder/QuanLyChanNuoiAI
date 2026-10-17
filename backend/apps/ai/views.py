from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.users.permissions import RoleActionPermission

from .reminders import generate_reminders
from .herd_summary import NOTICE, generate_herd_summary
from .growth_report import generate_growth_report
from .chat import answer_chat_question
from .serializers import ChatRequestSerializer, GrowthReportRequestSerializer, HerdSummaryRequestSerializer, ReminderRequestSerializer


class ChatView(APIView):
    permission_classes = [IsAuthenticated, RoleActionPermission]
    permission_resource = "ai"
    permission_action = "read"

    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = answer_chat_question(
            request.user, serializer.validated_data["question"], serializer.validated_data["history"],
        )
        return Response({"status": "success", **result})


class ReminderView(APIView):
    permission_classes = [IsAuthenticated, RoleActionPermission]
    permission_resource = "ai"
    permission_action = "read"

    def post(self, request):
        serializer = ReminderRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = generate_reminders(request.user, **serializer.validated_data)
        return Response({"status": "success", "feature": "reminders", "result": {"text": result["text"], "source_count": result["source_count"]}, "notice": result["notice"]})


class HerdSummaryView(APIView):
    permission_classes = [IsAuthenticated, RoleActionPermission]
    permission_resource = "ai"
    permission_action = "read"

    def post(self, request):
        serializer = HerdSummaryRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = generate_herd_summary(request.user, serializer.validated_data["herd_id"])
        return Response({"status": "success", "feature": "herd_summary", "result": result, "notice": NOTICE})


class GrowthReportView(APIView):
    permission_classes = [IsAuthenticated, RoleActionPermission]
    permission_resource = "ai"
    permission_action = "read"

    def post(self, request):
        serializer = GrowthReportRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = generate_growth_report(request.user, **serializer.validated_data)
        return Response({
            "status": "success",
            "feature": "growth_report",
            "result": {"text": result["text"], "source_count": result["source_count"], "metrics": result["metrics"]},
            "notice": result["notice"],
        })
