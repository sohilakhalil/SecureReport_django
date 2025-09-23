import json
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Report, CriminalInfo, Attachment
from .serializers import ReportNestedSerializer, ReportTrackingSerializer
from django.http import JsonResponse

def my_view(request):
    response = JsonResponse({"msg": "ok"})
    response["Access-Control-Allow-Origin"] = "https://securereport.netlify.app"
    return response



class ReportCreateNestedView(generics.CreateAPIView):
    """
    Create a new Report along with optional CriminalInfo and Attachments.
    Handles JSON parsing for criminals and differentiates audio/file attachments.
    """
    queryset = Report.objects.all()
    serializer_class = ReportNestedSerializer
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()

        # Parse 'criminal_infos' from JSON string, default to empty list if invalid
        criminal_infos = []
        if "criminal_infos" in data:
            try:
                criminal_infos = json.loads(data["criminal_infos"])
            except Exception:
                criminal_infos = []

        # Remove 'criminal_infos' from main data before saving the Report
        data.pop("criminal_infos", None)

        # Convert latitude and longitude to float, fallback to None if invalid
        for field in ["latitude", "longitude"]:
            value = data.get(field)
            if isinstance(value, list):
                value = value[0]
            try:
                data[field] = float(value)
            except (TypeError, ValueError):
                data[field] = None

        # Save main Report
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        report = serializer.save()

        # Save CriminalInfo objects in bulk if any
        criminal_objs = [
            CriminalInfo(report=report, **criminal) for criminal in criminal_infos
        ]
        CriminalInfo.objects.bulk_create(criminal_objs)

        # Save attachments, separating audio and other files
        files = request.FILES.getlist("attachments")
        attachments_to_create = []
        for f in files:
            filename = f.name.lower()
            if "audio" in filename or filename.endswith((".mp3", ".wav", ".webm", ".ogg")):
                attachments_to_create.append(Attachment(report=report, audio_recording=f))
            else:
                attachments_to_create.append(Attachment(report=report, file=f))
        Attachment.objects.bulk_create(attachments_to_create)

        # Return full Report data including nested criminals and attachments
        report_data = ReportNestedSerializer(report, context={"request": request}).data
        return Response(report_data, status=status.HTTP_201_CREATED)


class ReportListView(generics.ListAPIView):
    """List all reports, optionally including nested CriminalInfo and Attachments."""
    queryset = Report.objects.all()
    serializer_class = ReportNestedSerializer


class ReportDetailView(generics.RetrieveAPIView):
    """Retrieve a single report by ID with full details."""
    queryset = Report.objects.all()
    serializer_class = ReportNestedSerializer
    lookup_field = "id"


class ReportUpdateView(generics.UpdateAPIView):
    """
    Update Report fields.
    Currently only updates main Report data; nested CriminalInfo and Attachments
    can be supported later if needed.
    """
    queryset = Report.objects.all()
    serializer_class = ReportNestedSerializer
    lookup_field = "id"


class ReportDeleteView(generics.DestroyAPIView):
    """Delete a report by its ID."""
    queryset = Report.objects.all()
    serializer_class = ReportNestedSerializer
    lookup_field = "id"


class ReportTrackView(generics.RetrieveAPIView):
    """Retrieve a report using its tracking_code."""
    queryset = Report.objects.all()
    serializer_class = ReportTrackingSerializer
    lookup_field = "tracking_code"
