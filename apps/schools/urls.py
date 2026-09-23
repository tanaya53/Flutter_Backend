from django.urls import path
from .views import VerifySchoolIdView, CurrentSchoolView

urlpatterns = [
    path('verify-id/', VerifySchoolIdView.as_view(), name='verify-school-id'),
    path('current/', CurrentSchoolView.as_view(), name='current-school'),
]
