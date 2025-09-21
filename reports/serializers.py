from rest_framework import serializers
from .models import Report, CriminalInfo, Attachment


# Nested serializer for CriminalInfo
class CriminalInfoNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = CriminalInfo
        fields = ["name", "description", "other_info"]

# Nested serializer for Attachments
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


# Serializer for Report with nested criminal_infos and attachments
class ReportNestedSerializer(serializers.ModelSerializer):
    criminal_infos = CriminalInfoNestedSerializer(many=True, required=False)
    attachments = AttachmentNestedSerializer(many=True, required=False)

    class Meta:
        model = Report
        fields = [
            "id", "tracking_code", "location", "latitude", "longitude", "report_type",
            "incident_date", "report_details", "contact_info",
            "criminal_infos", "attachments"
        ]
        read_only_fields = ("id", "tracking_code")

    def create(self, validated_data):
        # Extract nested data
        criminal_data = validated_data.pop("criminal_infos", [])
        attachment_data = validated_data.pop("attachments", [])

        # Save main Report
        report = Report.objects.create(**validated_data)

        # Save related CriminalInfo objects in bulk
        criminal_objs = [CriminalInfo(report=report, **c) for c in criminal_data]
        CriminalInfo.objects.bulk_create(criminal_objs)

        # Save related Attachment objects
        attachment_objs = []
        for att in attachment_data:
            file_obj = att.get("file")
            audio_obj = att.get("audio_recording")
            if file_obj:
                attachment_objs.append(Attachment(report=report, file=file_obj))
            elif audio_obj:
                attachment_objs.append(Attachment(report=report, audio_recording=audio_obj))
        Attachment.objects.bulk_create(attachment_objs)

        return report  # Return the main report instance


# Serializer for tracking a report using tracking_code
class ReportTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ["id", "tracking_code", "case_status", "report_details", "report_type", "created_at"]
