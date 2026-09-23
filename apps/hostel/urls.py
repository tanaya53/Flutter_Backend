from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    HostelViewSet,
    RoomViewSet,
    AllocateBedView,
    LeaveRequestViewSet,
    ProcessLeaveView,
    HostelIncidentViewSet,
    MealViewSet,
    FoodStockViewSet,
    HostelSummaryView
)

router = DefaultRouter()
router.register(r'rooms', RoomViewSet, basename='hostel-rooms')
router.register(r'leaves', LeaveRequestViewSet, basename='hostel-leaves')
router.register(r'incidents', HostelIncidentViewSet, basename='hostel-incidents')
router.register(r'meals', MealViewSet, basename='hostel-meals')
router.register(r'food-stocks', FoodStockViewSet, basename='hostel-food-stocks')
router.register(r'', HostelViewSet, basename='hostels')

urlpatterns = [
    path('allocate-bed/', AllocateBedView.as_view(), name='allocate-bed'),
    path('process-leave/<int:pk>/', ProcessLeaveView.as_view(), name='process-leave'),
    path('summary/', HostelSummaryView.as_view(), name='hostel-summary'),
    path('', include(router.urls)),
]
