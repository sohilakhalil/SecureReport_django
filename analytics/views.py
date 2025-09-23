from django.http import JsonResponse
from .utils import get_combined_reports_dataframe


def filter_dataframe(df, year=None, location=None):
    """Apply filters to the dataframe based on query params."""
    if year:
        df = df[df['incident_date'].dt.year == int(year)]
    if location:
        df = df[df['location'].str.contains(location, case=False)]
    return df


def get_kpis(df):
    """Return KPIs from dataframe."""
    if df.empty:
        return {
            "total_reports": 0,
            "top_report_type": None,
            "solved_percentage": 0,
            "top_region": None
        }

    return {
        "total_reports": len(df),
        "top_report_type": df['report_type'].value_counts().idxmax(),
        "solved_percentage": (df['case_status'] == "تم الحل").mean() * 100,
        "top_region": df['location'].value_counts().idxmax()
    }


def get_charts(df):
    """Return charts data from dataframe.
    Charts include:
        - monthly_reports: Line chart (number of reports per month)
        - report_type_distribution: Bar chart (reports grouped by type)
        - case_status_distribution: Donut chart (reports grouped by status)
        - heatmap: Map chart (list of coordinates for reports)
    """
    if df.empty:
        return {
            "monthly_reports": {},
            "report_type_distribution": {},
            "case_status_distribution": {},
            "heatmap": []
        }

    # Line chart: monthly reports
    df['month'] = df['incident_date'].dt.to_period('M').astype(str)
    monthly_counts = df['month'].value_counts().sort_index().to_dict()

    return {
        "monthly_reports": monthly_counts,  # => Line chart
        "report_type_distribution": df['report_type'].value_counts().to_dict(),  # => Bar chart
        "case_status_distribution": df['case_status'].value_counts().to_dict(),  # => Donut chart
        "heatmap": df[['latitude', 'longitude']].dropna().to_dict(orient='records'),  # =>  Heatmap
    }

def dashboard_data(request):
    df = get_combined_reports_dataframe()

    # Apply filters
    df = filter_dataframe(
        df,
        year=request.GET.get("year"),
        location=request.GET.get("location")
    )

    data = {
        "kpis": get_kpis(df),
        "charts": get_charts(df)
    }
    return JsonResponse(data)