import uuid
from django.db import models

# Main Report table
class Report(models.Model):

    location = models.CharField(max_length=255)
    # location_link = models.URLField(max_length=500, blank=True, null=True)  # لينك جوجل مابس
    latitude = models.DecimalField(max_digits=18, decimal_places=15, null=True, blank=True)
    longitude = models.DecimalField(max_digits=18, decimal_places=15, null=True, blank=True)
    incident_date = models.DateField()
    report_details = models.TextField()
    contact_info = models.CharField(max_length=255, blank=True, null=True)  
    report_type = models.CharField(
        max_length=20,
        choices=[
            ('اعتداء', 'اعتداء'),
            ('ابتزاز', 'ابتزاز'),
            ('تحرش', 'تحرش'),
            ('سرقة', 'سرقة'),
            ('مشادة', 'مشادة'),
        ],
        default='اعتداء'
    )
    case_status = models.CharField(
        max_length=20,
        choices=[
        ('تم استلام البلاغ', 'تم استلام البلاغ'),
        ('قيد المراجعة', 'قيد المراجعة'),
        ('قيد المعالجة', 'قيد المعالجة'),
        ('تم الحل', 'تم الحل'),
        ('تم الإغلاق', 'تم الإغلاق'),
    ],
    default='تم استلام البلاغ'
)
    # Auto-generated tracking code for each report
    tracking_code = models.CharField(max_length=12, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Generate tracking code if not exists before saving."""
        if not self.tracking_code:
            self.tracking_code = uuid.uuid4().hex[:12].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tracking_code} - {self.case_status}"
    

# Table for criminal information related to a report
class CriminalInfo(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="criminal_infos")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)  
    other_info = models.TextField(blank=True, null=True)  

    def __str__(self):
        return self.name
    

# Table for attachments related to a report
class Attachment(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="attachments")
    audio_recording = models.FileField(upload_to="attachments/audio/", blank=True, null=True)  # => Audio files folder
    file = models.FileField(upload_to="attachments/files/", blank=True, null=True)  # => Other files folder
    def __str__(self):
        return f"Attachment for {self.report.tracking_code}"
