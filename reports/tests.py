import pandas as pd
from .models import Report


path = r"D:\summer2025\Digitopea\DIGITOPIA\backend\crime_report_system\analytics\data\fake_reports.csv"

def import_csv_to_reports(path):
    df = pd.read_csv(path)

    # تحويل التاريخ من نص لتاريخ
    df["incident_date"] = pd.to_datetime(df["incident_date"], errors="coerce")

    created_count = 0

    for _, row in df.iterrows():
        Report.objects.create(
            location=row.get("location"),
            location_link=row.get("location_link"),
            latitude=pd.to_numeric(row.get("latitude"), errors="coerce"),
            longitude=pd.to_numeric(row.get("longitude"), errors="coerce"),
            incident_date=row.get("incident_date"),
            report_details=row.get("report_details"),
            report_type=row.get("report_type"),
            case_status=row.get("case_status"),
            contact_info=row.get("contact_info", None) if "contact_info" in row else None,
            severity=None,  
            is_fake=True   
        )
        created_count += 1

    print(f"✅ Done! Inserted {created_count} reports into the database.")
