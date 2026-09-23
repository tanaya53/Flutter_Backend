from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DailyAttendanceViewSet,
    BulkAttendanceView,
    StudentAttendanceHistoryView,
    RepeatedAbsenteesView,
    AttendanceSummaryView,
    HostelAttendanceViewSet,
)

router = DefaultRouter()
router.register(r'hostel', HostelAttendanceViewSet, basename='hostel-attendance')
router.register(r'', DailyAttendanceViewSet, basename='daily-attendance')

urlpatterns = [
    path('bulk/', BulkAttendanceView.as_view(), name='attendance-bulk'),
    path('summary/', AttendanceSummaryView.as_view(), name='attendance-summary'),
    path('repeated-absentees/', RepeatedAbsenteesView.as_view(), name='attendance-repeated-absentees'),
    path('student/<int:student_id>/', StudentAttendanceHistoryView.as_view(), name='student-attendance-history'),
    path('', include(router.urls)),
]
