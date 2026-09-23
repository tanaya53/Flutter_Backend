from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnnouncementViewSet, MarkNotificationReadView

router = DefaultRouter()
router.register(r'', AnnouncementViewSet, basename='announcements')

urlpatterns = [
    path('mark-read/<int:announcement_id>/', MarkNotificationReadView.as_view(), name='mark-read'),
    path('', include(router.urls)),
]
