from django.urls import path
from .views import (
    ReportCreateNestedView,  #? => Unified form: create report + criminals + attachments
    ReportListView,
    ReportDetailView,
    ReportUpdateView,
    ReportDeleteView,
    ReportTrackView,
)

urlpatterns = [
    # Create a new report along with criminal info and attachments
    path('reports/new/', ReportCreateNestedView.as_view(), name='report-create-nested'),

    # List all reports
    path('reports/', ReportListView.as_view(), name='report-list'),

    # Retrieve a single report in detail
    path('reports/<int:id>/', ReportDetailView.as_view(), name='report-detail'),

    # Update a report
    path('reports/<int:id>/update/', ReportUpdateView.as_view(), name='report-update'),

    # Delete a report
    path('reports/<int:id>/delete/', ReportDeleteView.as_view(), name='report-delete'),

    # Track a report using tracking_code
    path('reports/track/<str:tracking_code>/', ReportTrackView.as_view(), name='report-track'),
]