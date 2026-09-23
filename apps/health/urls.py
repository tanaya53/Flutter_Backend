from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    HealthRecordViewSet,
    MedicalCheckupViewSet,
    VaccinationViewSet,
    EmergencyMedicalAlertViewSet,
    HealthSummaryView,
    StudentHealthDetailView
)

router = DefaultRouter()
router.register(r'profiles', HealthRecordViewSet, basename='health-profiles')
router.register(r'checkups', MedicalCheckupViewSet, basename='medical-checkups')
router.register(r'vaccinations', VaccinationViewSet, basename='vaccinations')
router.register(r'alerts', EmergencyMedicalAlertViewSet, basename='health-alerts')

urlpatterns = [
    path('summary/', HealthSummaryView.as_view(), name='health-summary'),
    path('student/<int:student_id>/', StudentHealthDetailView.as_view(), name='student-health-detail'),
    path('', include(router.urls)),
]
