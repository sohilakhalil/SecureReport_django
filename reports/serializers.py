import json
import bleach
from rest_framework import serializers
from .models import Report, CriminalInfo, Attachment

# --------------------Nested serializer for CriminalInfo-----------------------------
class CriminalInfoNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = CriminalInfo
        fields = ["name", "description", "other_info"]

# ------------------Nested serializer for Attachments------------------------------
class AttachmentNestedSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    class Meta:
        model = Attachment
        fields = ["type", "url"]

    def get_type(self, obj):
        """Return 'audio' if the attachment is audio, otherwise 'file'."""
        return "audio" if obj.audio_recording else "file"

    def get_url(self, obj):
        """Build absolute URL for the file or audio, if request context is available."""
        request = self.context.get("request")
        file_obj = obj.file or obj.audio_recording
        if not file_obj:
            return None
        url = file_obj.url
        return request.build_absolute_uri(url) if request else url

# -------------------Serializer for Report with nested criminal_infos and attachments---------------------
class ReportNestedSerializer(serializers.ModelSerializer):
    criminal_infos = CriminalInfoNestedSerializer(many=True, required=False)
    attachments = AttachmentNestedSerializer(many=True, required=False)

    class Meta:
        model = Report
        fields = [
            "id", "tracking_code","status", "location", "latitude", "location_link", "longitude", "report_type",
            "incident_date", "report_details", "contact_info", "severity",
            "criminal_infos", "attachments", "created_at"
        ]
        read_only_fields = ("id", "tracking_code")

# ----------------------Sanitization methods----------------------------------------------------------
    def _sanitize(self, value):
        if not value: 
            return value
        return bleach.clean(str(value), tags=[], attributes={}, strip=True)

    def validate_location(self, value):
        return self._sanitize(value)

    def validate_report_details(self, value):
        return self._sanitize(value)

    def validate_contact_info(self, value):
        return self._sanitize(value)

# ------------------------Create method with nested criminal_infos and attachments-------------------------
    def create(self, validated_data):
        criminal_infos_data = self.initial_data.get("criminal_infos", [])
        attachments_files = self.context['request'].FILES.getlist("attachments")

        # Create Report
        report = Report.objects.create(**validated_data)

        # Create CriminalInfo
        try:
            criminal_infos_data = json.loads(criminal_infos_data)
        except Exception:
            criminal_infos_data = []
        CriminalInfo.objects.bulk_create([CriminalInfo(report=report, **c) for c in criminal_infos_data])

        # Create Attachments
        attachments_to_create = []
        for f in attachments_files:
            if "audio" in f.name.lower() or f.name.lower().endswith((".mp3", ".wav", ".webm", ".ogg")):
                attachments_to_create.append(Attachment(report=report, audio_recording=f))
            else:
                attachments_to_create.append(Attachment(report=report, file=f))
        Attachment.objects.bulk_create(attachments_to_create)

        return report

# ---------------------------Serializer for tracking a report using tracking_code---------------------------------
class ReportTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ["id", "tracking_code", "status", "report_type", "created_at"]

# -----------------------------Serializer for read-only view for Viewer role---------------------------------------
class ReportViewerSerializer(serializers.ModelSerializer):
    """
    Limited serializer for Viewer role to see only basic report info.
    """
    class Meta:
        model = Report
        fields = ["id", "tracking_code", "status", "report_type", "created_at"]
