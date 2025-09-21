import pandas as pd
from reports.models import Report
from django.conf import settings

# Expected schema for reports data
EXPECTED_COLS = [
    "location",
    "incident_date",
    "report_details",
    "report_type",
    "case_status",
    "latitude",
    "longitude"
]
# Text columns that require trimming/cleaning
TEXT_COLS = ["location", "report_details", "report_type", "case_status"]


def get_csv_path(csv_path=None):
    """
    Return the final CSV path.
    If no path is provided, fallback to settings.DATA_FILE.
    """
    return csv_path or settings.DATA_FILE


def clean_reports_dataframe(df):
    """
    Clean and normalize the reports DataFrame:
      - Convert columns to the correct data types
      - Drop duplicates
      - Strip whitespace from text fields
    """
    # Convert to proper data types
    df['incident_date'] = pd.to_datetime(df['incident_date'], errors='coerce')
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')

    # Remove duplicates
    df = df.drop_duplicates()

    # Trim whitespace in text columns
    for col in TEXT_COLS:
        df[col] = df[col].astype(str).str.strip()

    return df


def get_db_reports_dataframe():
    """
    Fetch reports from the database and return as a cleaned DataFrame.
    """
    qs = Report.objects.values(*EXPECTED_COLS)
    df = pd.DataFrame(list(qs))
    return clean_reports_dataframe(df)


def get_fake_reports_dataframe(csv_path=None):
    """
    Fetch reports from a CSV file and return as a cleaned DataFrame.
    Safely handles missing files and empty CSVs.
    """
    csv_path = get_csv_path(csv_path)
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        return pd.DataFrame(columns=EXPECTED_COLS)
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=EXPECTED_COLS)
    
    # Keep only the expected schema
    df = df[EXPECTED_COLS]
    return clean_reports_dataframe(df)


def get_combined_reports_dataframe(csv_path=None):
    """
    Merge reports from both the database and CSV into a single DataFrame.
    Ensures consistent schema and data cleaning.
    """
    db_df = get_db_reports_dataframe()
    fake_df = get_fake_reports_dataframe(csv_path)

    combined_df = pd.concat([db_df, fake_df], ignore_index=True)
    return clean_reports_dataframe(combined_df)
