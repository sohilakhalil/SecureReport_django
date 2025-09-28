from django.urls import path
from .views import (
    ReportListCreateView,
    ReportRetrieveUpdateDestroyView,
    ReportTrackView,
    ReportArchiveListView,
)

urlpatterns = [
    # GET list / POST create
    path('reports/', ReportListCreateView.as_view(), name='report-list-create'),

    # GET detail / PATCH update / DELETE
    path('reports/<int:id>/', ReportRetrieveUpdateDestroyView.as_view(), name='report-detail-update-delete'),

    # Track report by tracking code
    path('reports/track/<str:tracking_code>/', ReportTrackView.as_view(), name='report-track'),

    path('reports/archive/', ReportArchiveListView.as_view(), name='report-archive-list'),
]