from rest_framework import generics, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .models import Report
from .serializers import ReportNestedSerializer, ReportTrackingSerializer, ReportViewerSerializer
# from .ml_model import predict_severity

# ----------------------------- Helper ------------------------------------
def is_active_user(user):
    return user.is_authenticated and user.status == 'active'

# ----------------------------List & create reports--------------------------
class ReportListCreateView(generics.ListCreateAPIView):
    """
    Create a new Report along with optional CriminalInfo and Attachments.
    Handles JSON parsing for criminals and differentiates audio/file attachments.
    """
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        instance = serializer.save()
        # ------------------ AI Model Part (Commented for GitHub) ------------------
        # if instance.report_details:
        #     from .ml_model import predict_severity
        #     instance.severity = predict_severity(instance.report_details)
        #     instance.save(update_fields=["severity"])
        # --------------------------------------------------------------------------

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.AllowAny()]  # => Open to everyone
        return [permissions.IsAuthenticated()]  # => GET requires authentication

    def get_serializer_class(self):
        """
        Use limited serializer for Viewer role, full serializer for Admin/Employee.
        """
        user = self.request.user
        if user.is_authenticated and user.role == "Viewer":
            return ReportViewerSerializer
        return ReportNestedSerializer

    def get_queryset(self):
        """
        Return reports based on user role.
        Admin/Employee: all reports.
        Viewer: all reports (serializer limits fields).
        Anonymous: none.
        """
        user = self.request.user
        qs = Report.objects.exclude(status__in=["تم الحل", "تم الإغلاق"]).order_by('id')

        if not is_active_user(user):
            return Report.objects.none()  # inactive or anonymous users see nothing
        return qs

# -------------------------------Archived reports------------------------------------------
class ReportArchiveListView(generics.ListAPIView):
    """
    List reports that are archived (status solved/closed).
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        user = self.request.user
        if user.role == "Viewer":
            return ReportViewerSerializer
        return ReportNestedSerializer

    def get_queryset(self):
        user = self.request.user
        if not is_active_user(user):
            return Report.objects.none()
        return Report.objects.filter(status__in=["تم الحل", "تم الإغلاق"]).order_by('id')

# -----------------------------Retrieve, update, or delete a report----------------------------
class ReportRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific report by id.
    """
    queryset = Report.objects.all()
    lookup_field = "id"

    def get_serializer_class(self):
        user = self.request.user
        if user.role == "Viewer":
            return ReportViewerSerializer
        return ReportNestedSerializer

    def get_permissions(self):
        return [permissions.IsAuthenticated()]

    def patch(self, request, *args, **kwargs):
        """
        Admin and Employee can update all fields.
        Viewer cannot update.
        """
        user = request.user
        if not is_active_user(user):
            return Response({"detail": "Inactive user."}, status=status.HTTP_403_FORBIDDEN)
        if user.role in ["Admin", "Employee"]:
            return super().partial_update(request, *args, **kwargs)
        return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)


    def delete(self, request, *args, **kwargs):
        """
        Admin and Employee can delete reports.
        Viewer cannot delete.
        """
        user = request.user
        if not is_active_user(user):
            return Response({"detail": "Inactive user."}, status=status.HTTP_403_FORBIDDEN)
        if user.role in ["Admin", "Employee"]:
            return super().destroy(request, *args, **kwargs)
        return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

# ------------------------Track a report using tracking_code-----------------------
class ReportTrackView(generics.RetrieveAPIView):
    """
    Retrieve a report using its tracking_code.
    Used by anonymous users to track their report status.
    """
    queryset = Report.objects.all()
    serializer_class = ReportTrackingSerializer
    lookup_field = "tracking_code"
    permission_classes = [permissions.AllowAny]  # => Open to everyone
