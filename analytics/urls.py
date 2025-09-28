from django.urls import path
from . import views

urlpatterns = [
    # Classic dashboard
    path("analytics/stats/", views.dashboard_data, name="dashboard_data"),
    
    # Recent dashboard
    path("analytics/recent/", views.dashboard_recent_data, name="dashboard_recent_data"),

    path("analytics/site_stats/", views.public_site_stats, name="public_site_stats"),
]
