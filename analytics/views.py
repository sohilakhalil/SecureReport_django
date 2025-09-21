from django.http import JsonResponse
import pandas as pd
from .utils import get_combined_reports_dataframe

def filter_dataframe(df, year=None, month=None, day=None, location=None):
    """Apply general filters: year, month, day, location."""
    if year:
        df = df[df['incident_date'].dt.year == int(year)]
    if month:
        df = df[df['incident_date'].dt.month == int(month)]
    if day:
        df = df[df['incident_date'].dt.day == int(day)]
    if location:
        df = df[df['location'].str.contains(location, case=False)]
    return df

def calculate_trend(filtered_count, total_count, context_counts=None):
    """Return trend direction and percentage."""
    if total_count == 0:
        return {"percentage": 0.0, "trend": "neutral"}

    percentage = round((filtered_count / total_count) * 100, 2)
    trend = "neutral"
    if context_counts and len(context_counts) > 0:
        mean_context = sum(context_counts) / len(context_counts)
        trend = "increase" if filtered_count > mean_context else "decrease"
    return {"percentage": percentage, "trend": trend}

def get_kpis(filtered_df, full_df, filter_mode=None):
    """Return KPIs with count, percentage, and trend."""
    total_reports = len(full_df)

    def calc(status):
        count = int((filtered_df['case_status'] == status).sum())

        # حساب trend حسب الفلتر
        context_counts = None
        if filter_mode == "day":
            context_counts = full_df.groupby(full_df['incident_date'].dt.day)['case_status'].apply(lambda x: (x==status).sum()).tolist()
        elif filter_mode == "week":
            week_numbers = full_df['incident_date'].dt.isocalendar().week
            context_counts = full_df.groupby(week_numbers)['case_status'].apply(lambda x: (x==status).sum()).tolist()
        elif filter_mode == "month":
            months = full_df['incident_date'].dt.month
            context_counts = full_df.groupby(months)['case_status'].apply(lambda x: (x==status).sum()).tolist()

        return {
            "count": count,
            **calculate_trend(count, total_reports, context_counts)
        }

    solved = calc("تم الحل")

    return {
        "total_reports": len(filtered_df),
        "new_reports": calc("تم استلام البلاغ"),
        "under_review_reports": calc("قيد المراجعة"),
        "solved_reports": solved,
        "solved_percentage": round((solved["count"] / total_reports) * 100, 2) if total_reports > 0 else 0,
        "top_report_type": str(filtered_df['report_type'].value_counts().idxmax()) if not filtered_df.empty else None,
        "top_region": str(filtered_df['location'].value_counts().idxmax()) if not filtered_df.empty else None,
    }

def get_time_series(df, filter_mode="month"):
    """Return bar chart data for day/week/month filters."""
    if df.empty:
        return {}

    now = pd.Timestamp.now().normalize()
    df = df.copy()
    result = {}

    if filter_mode == "day":
        # آخر 7 أيام
        start_date = now - pd.Timedelta(days=6)
        df = df[df['incident_date'] >= start_date]
        df['day_name'] = df['incident_date'].dt.day_name(locale='ar')
        # ترتيب الأيام
        day_order = ["الاثنين","الثلاثاء","الأربعاء","الخميس","الجمعة","السبت","الأحد"]
        counts = df['day_name'].value_counts().reindex(day_order, fill_value=0).to_dict()
        result = counts

    elif filter_mode == "week":
        # الأسبوع مقسوم لأربعة أسابيع من الشهر الحالي
        start_month = now.replace(day=1)
        df = df[df['incident_date'] >= start_month]

        def get_week_of_month(date):
            return ((date.day - 1) // 7) + 1  # 1-4

        df['week_of_month'] = df['incident_date'].apply(get_week_of_month)
        week_labels = [f"الأسبوع {i}" for i in range(1, 5)]
        counts_dict = df['week_of_month'].value_counts().to_dict()
        result = {label: counts_dict.get(i, 0) for i, label in enumerate(week_labels, start=1)}

    elif filter_mode == "month":
        # آخر 12 شهر
        df['month'] = df['incident_date'].dt.month
        month_names = {
            1:"يناير",2:"فبراير",3:"مارس",4:"أبريل",5:"مايو",6:"يونيو",
            7:"يوليو",8:"أغسطس",9:"سبتمبر",10:"أكتوبر",11:"نوفمبر",12:"ديسمبر"
        }
        # ترتيب الشهور من يناير → ديسمبر
        counts_dict = df['month'].value_counts().to_dict()
        result = {month_names[i]: counts_dict.get(i, 0) for i in range(1, 13)}

    return result


def get_charts(df):
    """Return donut chart (report type) and heatmap."""
    if df.empty:
        return {
            "report_type_distribution": {},
            "case_status_distribution": {},
            "heatmap": [],
        }

    # توحيد case_status
    status_map = {"received": "تم استلام البلاغ","pending": "قيد المراجعة","تحت المراجعة": None}
    df['case_status'] = df['case_status'].map(lambda x: status_map.get(x, x))

    return {
        "report_type_distribution": {str(k): int(v) for k,v in df['report_type'].value_counts().to_dict().items()},
        "case_status_distribution": {str(k): int(v) for k,v in df['case_status'].value_counts().to_dict().items()},
        "heatmap": df[['latitude','longitude']].dropna().astype(float).to_dict(orient='records')
    }

def dashboard_data(request):
    full_df = get_combined_reports_dataframe()
    # الفلترة الأساسية حسب السنة والموقع
    filtered_df = filter_dataframe(
        full_df,
        year=request.GET.get("year"),
        month=request.GET.get("month"),
        day=request.GET.get("day"),
        location=request.GET.get("location"),
    )

    filter_mode = request.GET.get("filter_mode","month") # day/week/month

    data = {
        "kpis": get_kpis(filtered_df, full_df, filter_mode),
        "charts": {
            "time_series": get_time_series(filtered_df, filter_mode),  # bar chart
            **get_charts(filtered_df),  # donut + heatmap
        }
    }
    return JsonResponse(data)
