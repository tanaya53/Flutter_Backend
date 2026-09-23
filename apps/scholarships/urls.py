from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ScholarshipViewSet, WelfareSchemeViewSet, ScholarshipSummaryView

router = DefaultRouter()
router.register(r'schemes', WelfareSchemeViewSet, basename='welfare-schemes')
router.register(r'', ScholarshipViewSet, basename='scholarships')

urlpatterns = [
    path('summary/', ScholarshipSummaryView.as_view(), name='scholarship-summary'),
    path('', include(router.urls)),
]
