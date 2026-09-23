from django.urls import path
from .views import (
    PrincipalDashboardAnalyticsView,
    ExportAttendanceReportView,
    ExportStudentRosterView,
    ExportHostelReportView,
    ExportInventoryReportView,
    ExportScholarshipReportView,
)

urlpatterns = [
    path('analytics/', PrincipalDashboardAnalyticsView.as_view(), name='principal-analytics'),
    path('attendance/', ExportAttendanceReportView.as_view(), name='report-attendance'),
    path('students/', ExportStudentRosterView.as_view(), name='report-students'),
    path('hostel/', ExportHostelReportView.as_view(), name='report-hostel'),
    path('inventory/', ExportInventoryReportView.as_view(), name='report-inventory'),
    path('scholarships/', ExportScholarshipReportView.as_view(), name='report-scholarships'),
]
