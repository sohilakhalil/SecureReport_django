from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.http import JsonResponse
from .utils import get_db_reports_dataframe, filter_dataframe, get_kpis, get_charts, compute_recent_kpis, compute_recent_charts

# ---------------------------- Custom Permission ----------------------------
def is_active_user(user):
    return user.is_authenticated and user.status == 'active'

# ----------------------------- Classic Dashboard --------------------------------
@api_view(['GET'])
def dashboard_data(request):
    """
    Classic Dashboard API.
    - Public 'site_stats' if user not authenticated or inactive
    - Other KPIs/charts require active user
    """
    df = get_db_reports_dataframe()
    df = filter_dataframe(df, year=request.GET.get("year"), location=request.GET.get("location"))

    full_kpis = get_kpis(df)

    user = request.user
    if is_active_user(user):
        return Response({
            "kpis": full_kpis,
            "charts": get_charts(df),
        })
    else:
        # Public access returns empty KPIs/charts
        return Response({
            "kpis": {},
            "charts": {},
        })

# --------------------------- Recent Dashboard ------------------------------------
@api_view(['GET'])
def dashboard_recent_data(request):
    """
    Recent Dashboard API.
    - Only active users can see KPIs and charts
    - Public access returns empty KPIs/charts
    """
    df = get_db_reports_dataframe()
    df = filter_dataframe(df, year=request.GET.get("year"), location=request.GET.get("location"))
    period = request.GET.get("period", "daily")

    user = request.user
    if is_active_user(user):
        return Response({
            "kpis": compute_recent_kpis(df),
            "charts": compute_recent_charts(df, period)
        })
    else:
        return Response({
            "kpis": {},
            "charts": {}
        })

# --------------------------------Public Site Stats -------------------------------------------------
@api_view(['GET'])
@permission_classes([AllowAny])
def public_site_stats(request):
    """
    Public site stats endpoint.
    No authentication required.
    Computes stats based on all reports.
    """
    df = get_db_reports_dataframe()
    
    data = {
        "site_stats": {
            "received_reports": len(df[df['status'] == "تم استلام البلاغ"]),
            "in_progress_reports": len(df[df['status'] == "قيد المعالجة"]),
            "closed_reports": len(df[df['status'] == "تم الإغلاق"]),
            "collaborating_entities": 20  # fixed value
        }
    }
    return JsonResponse(data)
