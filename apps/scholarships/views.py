from rest_framework import viewsets, views, status, permissions
from rest_framework.response import Response
from django.db.models import Sum, Count
from .models import Scholarship, WelfareScheme
from .serializers import ScholarshipSerializer, WelfareSchemeSerializer
from apps.accounts.permissions import IsApprovedUser, SameSchoolPermission

class ScholarshipViewSet(viewsets.ModelViewSet):
    serializer_class = ScholarshipSerializer
    permission_classes = [IsApprovedUser, SameSchoolPermission]

    def get_queryset(self):
        qs = Scholarship.objects.filter(school=self.request.user.school)
        student_id = self.request.query_params.get('student_id')
        if student_id:
            qs = qs.filter(student_id=student_id)
        status_param = self.request.query_params.get('status')
        if status_param:
            qs = qs.filter(status=status_param.upper())
        return qs

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)

class WelfareSchemeViewSet(viewsets.ModelViewSet):
    serializer_class = WelfareSchemeSerializer
    permission_classes = [IsApprovedUser, SameSchoolPermission]

    def get_queryset(self):
        return WelfareScheme.objects.filter(school=self.request.user.school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)

class ScholarshipSummaryView(views.APIView):
    """
    Dashboard metrics for Scholarships & Welfare Distribution.
    """
    permission_classes = [IsApprovedUser]

    def get(self, request):
        school = request.user.school
        scholarships = Scholarship.objects.filter(school=school)

        total_applications = scholarships.count()
        approved_count = scholarships.filter(status__in=['APPROVED', 'DISTRIBUTED']).count()
        distributed_count = scholarships.filter(status='DISTRIBUTED').count()
        pending_count = scholarships.filter(status__in=['PENDING', 'SUBMITTED', 'UNDER_REVIEW']).count()
        total_funds_disbursed = scholarships.filter(status='DISTRIBUTED').aggregate(Sum('amount'))['amount__sum'] or 0.0

        schemes = WelfareScheme.objects.filter(school=school)
        schemes_in_progress = schemes.filter(status='IN_PROGRESS').count()

        return Response({
            'total_scholarship_applications': total_applications,
            'approved_count': approved_count,
            'distributed_count': distributed_count,
            'pending_review_count': pending_count,
            'total_funds_disbursed': float(total_funds_disbursed),
            'active_welfare_schemes': schemes_in_progress,
        })
