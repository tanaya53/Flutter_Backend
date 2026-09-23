from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StudentViewSet,
    MyStudentsView,
    MyChildView,
    AcademicRemarkViewSet,
    StudentConcernViewSet
)

router = DefaultRouter()
router.register(r'remarks', AcademicRemarkViewSet, basename='academic-remarks')
router.register(r'concerns', StudentConcernViewSet, basename='student-concerns')
router.register(r'', StudentViewSet, basename='students')

urlpatterns = [
    path('my-students/', MyStudentsView.as_view(), name='my-students'),
    path('my-child/', MyChildView.as_view(), name='my-child'),
    path('', include(router.urls)),
]
