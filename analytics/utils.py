import pandas as pd
from datetime import timedelta
from reports.models import Report

EXPECTED_COLS = [
    "location",
    "incident_date",
    "report_details",
    "report_type",
    "status",
    "latitude",
    "longitude",
    "severity",
    "created_at",
]

TEXT_COLS = ["location", "report_details", "report_type", "status"]

def clean_reports_dataframe(df):
    df['incident_date'] = pd.to_datetime(df['incident_date'], errors='coerce')
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
    df = df.drop_duplicates()
    for col in TEXT_COLS:
        df.loc[:, col] = df[col].astype(str).str.strip()
    return df

def get_db_reports_dataframe():
    qs = Report.objects.values(*EXPECTED_COLS)
    df = pd.DataFrame(list(qs))
    return clean_reports_dataframe(df)

def get_combined_reports_dataframe():
    # For future use; currently same as DB
    return get_db_reports_dataframe()


def filter_dataframe(df, year=None, location=None):
    if year:
        df = df[df['incident_date'].dt.year == int(year)]
    if location:
        df = df[df['location'].str.contains(location, case=False)]
    return df

# --------------------------------- Classic Dashboard Helpers --------------------------------------
def get_kpis(df):
    if df.empty:
        return {
            "total_reports": 0,
            "top_report_type": None,
            "solved_percentage": 0,
            "top_region": None,
        }

    return {
        "total_reports": len(df),
        "top_report_type": df['report_type'].value_counts().idxmax(),
        "solved_percentage": (df['status'] == "تم الحل").mean() * 100,
        "top_region": df['location'].value_counts().idxmax(),
    }


def get_charts(df):
    if df.empty:
        return {"monthly_reports": {}, "report_type_distribution": {}, "case_status_distribution": {}, "heatmap": []}


    df['month_num'] = df['incident_date'].dt.month
    month_ar = {
        1: "يناير", 2: "فبراير", 3: "مارس", 4: "أبريل",
        5: "مايو", 6: "يونيو", 7: "يوليو", 8: "أغسطس",
        9: "سبتمبر", 10: "أكتوبر", 11: "نوفمبر", 12: "ديسمبر"
    }
    df['month'] = df['month_num'].map(month_ar)

    month_order = ["يناير","فبراير","مارس","أبريل","مايو","يونيو",
                   "يوليو","أغسطس","سبتمبر","أكتوبر","نوفمبر","ديسمبر"]

    monthly_counts = df['month'].value_counts().reindex(month_order, fill_value=0).to_dict()

    return {
        "monthly_reports": monthly_counts,
        "report_type_distribution": df['report_type'].value_counts().to_dict(),
        "case_status_distribution": df['status'].value_counts().to_dict(),
        "heatmap": df[['latitude', 'longitude']].dropna().to_dict(orient='records')
    }


# -------------------------- Recent Dashboard Helpers ----------------------------------------
def compute_recent_kpis(df):
    if df.empty:
        return {
            "total_reports": {"value": 0, "change": 0, "trend": "لا تغيير"},
            "new_reports": {"value": 0, "change": 0, "trend": "لا تغيير"},
            "under_review": {"value": 0, "change": 0, "trend": "لا تغيير"},
            "critical_reports": {"value": 0, "change": 0, "trend": "لا تغيير"},
        }

    today = df['incident_date'].max().normalize()
    four_months_ago = today - pd.DateOffset(months=4)
    four_months_before_that = four_months_ago - pd.DateOffset(months=4)
    yesterday = today - timedelta(days=1)
    day_before_yesterday = yesterday - timedelta(days=1)

    def calc_change(current, previous):
        if previous == 0:
            return (0, "لا تغيير") if current == 0 else (100, "زيادة")
        change = ((current - previous) / previous) * 100
        trend = "زيادة" if change > 0 else "انخفاض" if change < 0 else "لا تغيير"
        return round(abs(change), 2), trend


    # --- Total Reports KPI ---
    total_reports_value = len(df)
    recent_4m = len(df[df['incident_date'] >= four_months_ago])
    prev_4m = len(df[(df['incident_date'] >= four_months_before_that) & (df['incident_date'] < four_months_ago)])
    total_change, total_trend = calc_change(recent_4m, prev_4m)

    # --- New Reports KPI ---
    new_reports_value = len(df[df['status'] == "تم استلام البلاغ"])
    new_prev = len(df[df['incident_date'].dt.date == yesterday.date()])
    new_change, new_trend = calc_change(new_reports_value, new_prev)

    # --- Under Review KPI ---
    under_review_value = len(df[df['status'] == "قيد المراجعة"])
    under_recent = len(df[(df['status'] == "قيد المراجعة") & (df['incident_date'] >= four_months_ago)])
    under_prev = len(df[(df['status'] == "قيد المراجعة") & (df['incident_date'] >= four_months_before_that) & (df['incident_date'] < four_months_ago)])
    under_change, under_trend = calc_change(under_recent, under_prev)

    # --- Critical Reports KPI ---
    critical_value = len(df[df['severity'] == "حرج"])
    critical_recent = len(df[(df['severity'] == "حرج") & (df['incident_date'].dt.date == today.date())])
    critical_prev = len(df[(df['severity'] == "حرج") & (df['incident_date'].dt.date == yesterday.date())])
    critical_change, critical_trend = calc_change(critical_recent, critical_prev)

    return {
        "total_reports": {"value": total_reports_value, "change": total_change, "trend": total_trend},
        "new_reports": {"value": new_reports_value, "change": new_change, "trend": new_trend},
        "under_review": {"value": under_review_value, "change": under_change, "trend": under_trend},
        "critical_reports": {"value": critical_value, "change": critical_change, "trend": critical_trend},
    }


def compute_recent_charts(df, period="daily"):
    if df.empty:
        return {"bar_chart": {}, "status_distribution": {}, "heatmap": []}

    df_filtered = df.copy()

    # Select column by period
    if period == "daily":
        date_col = 'created_at'
    else:  # weekly أو monthly
        date_col = 'incident_date'

    # Convert column to Cairo time to avoid wrong day problems
    if df_filtered[date_col].dt.tz is not None:
        df_filtered[date_col] = df_filtered[date_col].dt.tz_convert(None)

    if period == "daily":
        # Convert to UTC then Cairo timezone
        df_filtered[date_col] = df_filtered[date_col].dt.tz_localize('UTC').dt.tz_convert('Africa/Cairo')
        today = pd.Timestamp.today(tz='Africa/Cairo').normalize()
        start_date = today - pd.Timedelta(days=6)
        df_filtered = df_filtered[df_filtered[date_col] >= start_date]

        # Translation of days into Arabic
        en_to_ar_days = {
            "Monday": "الاثنين",
            "Tuesday": "الثلاثاء",
            "Wednesday": "الأربعاء",
            "Thursday": "الخميس",
            "Friday": "الجمعة",
            "Saturday": "السبت",
            "Sunday": "الأحد"
        }
        df_filtered['bucket'] = df_filtered[date_col].dt.day_name().map(en_to_ar_days)
        day_order = ["الاثنين","الثلاثاء","الأربعاء","الخميس","الجمعة","السبت","الأحد"]
        bar_chart = df_filtered['bucket'].value_counts().reindex(day_order, fill_value=0).to_dict()

    elif period == "weekly":
        today = pd.Timestamp.today().normalize()
        start_date = today - pd.Timedelta(weeks=4)
        df_filtered = df_filtered[df_filtered[date_col] >= start_date]

        df_filtered['week_number'] = ((today - df_filtered[date_col]).dt.days // 7 + 1)
        df_filtered['bucket'] = "الأسبوع " + df_filtered['week_number'].astype(str)
        week_order = ["الأسبوع 4","الأسبوع 3","الأسبوع 2","الأسبوع 1"]  # ترتيب من الأقدم للأحدث
        bar_chart = df_filtered['bucket'].value_counts().reindex(week_order, fill_value=0).to_dict()

    else:  # monthly
        today = pd.Timestamp.today().normalize()
        start_date = today - pd.DateOffset(months=12)
        df_filtered = df_filtered[df_filtered[date_col] >= start_date]

        month_ar = {
            1: "يناير", 2: "فبراير", 3: "مارس", 4: "أبريل",
            5: "مايو", 6: "يونيو", 7: "يوليو", 8: "أغسطس",
            9: "سبتمبر", 10: "أكتوبر", 11: "نوفمبر", 12: "ديسمبر"
        }
        df_filtered['bucket'] = df_filtered[date_col].dt.month.map(month_ar)
        month_order = ["يناير","فبراير","مارس","أبريل","مايو","يونيو",
                       "يوليو","أغسطس","سبتمبر","أكتوبر","نوفمبر","ديسمبر"]
        bar_chart = df_filtered['bucket'].value_counts().reindex(month_order, fill_value=0).to_dict()

    # Distribution of cases
    status_distribution = df_filtered['status'].value_counts().to_dict()

    # heatmap
    heatmap = df[['latitude', 'longitude']].dropna().to_dict(orient='records')

    return {
        "bar_chart": bar_chart,
        "status_distribution": status_distribution,
        "heatmap": heatmap
    }
