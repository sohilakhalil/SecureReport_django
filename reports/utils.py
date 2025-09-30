import pandas as pd
from reports.models import Report

def import_csv_to_reports(path):
    """
    Import fake reports from a CSV file into the Report model.
    Each row becomes a new Report with is_fake=True.
    """
    try:
        df = pd.read_csv(path)
    except Exception as e:
        print(f"❌ Failed to read CSV: {e}")
        return

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
            status=row.get("status"),
            contact_info=row.get("contact_info", None) if "contact_info" in row else None,
            severity=None,  
            is_fake=True   
        )
        created_count += 1

    print(f"✅ Done! Inserted {created_count} fake reports.")


# python manage.py shell
# from reports.utils import import_csv_to_reports

# import_csv_to_reports(r"D:\summer2025\Digitopea\DIGITOPIA\backend\crime_report_system\analytics\data\fake_reports.csv")


# from reports.models import Report
# updated_count = Report.objects.filter(status="تم الاغلاق").update(status="تم الإغلاق")
# print(f"✅ Done! Updated {updated_count} reports.")
