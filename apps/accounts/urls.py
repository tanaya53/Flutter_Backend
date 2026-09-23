from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterSchoolView,
    RegisterUserView,
    LoginView,
    UserProfileView,
    ListJoinRequestsView,
    ProcessJoinRequestView,
    StaffListView,
)

urlpatterns = [
    path('register-school/', RegisterSchoolView.as_view(), name='register-school'),
    path('register-user/', RegisterUserView.as_view(), name='register-user'),
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('join-requests/', ListJoinRequestsView.as_view(), name='join-requests-list'),
    path('approve-user/<int:pk>/', ProcessJoinRequestView.as_view(), name='approve-user'),
    path('staff/', StaffListView.as_view(), name='staff-list'),
]
