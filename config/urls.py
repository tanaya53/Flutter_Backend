"""
URL configuration for Mazi Shala project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/schools/', include('apps.schools.urls')),
    path('api/students/', include('apps.students.urls')),
    path('api/attendance/', include('apps.attendance.urls')),
    path('api/health/', include('apps.health.urls')),
    path('api/hostel/', include('apps.hostel.urls')),
    path('api/scholarships/', include('apps.scholarships.urls')),
    path('api/inventory/', include('apps.inventory.urls')),
    path('api/announcements/', include('apps.announcements.urls')),
    path('api/reports/', include('apps.reports.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
