from rest_framework import viewsets, views, permissions, status
from rest_framework.response import Response
from django.utils import timezone
from .models import HealthRecord, MedicalCheckup, Vaccination, EmergencyMedicalAlert
from .serializers import (
    HealthRecordSerializer,
    MedicalCheckupSerializer,
    VaccinationSerializer,
    EmergencyMedicalAlertSerializer
)
from apps.accounts.permissions import IsApprovedUser, SameSchoolPermission
from apps.students.models import Student

class HealthRecordViewSet(viewsets.ModelViewSet):
    serializer_class = HealthRecordSerializer
    permission_classes = [IsApprovedUser, SameSchoolPermission]

    def get_queryset(self):
        qs = HealthRecord.objects.filter(school=self.request.user.school)
        student_id = self.request.query_params.get('student_id')
        if student_id:
            qs = qs.filter(student_id=student_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)

class MedicalCheckupViewSet(viewsets.ModelViewSet):
    serializer_class = MedicalCheckupSerializer
    permission_classes = [IsApprovedUser, SameSchoolPermission]

    def get_queryset(self):
        qs = MedicalCheckup.objects.filter(school=self.request.user.school)
        student_id = self.request.query_params.get('student_id')
        if student_id:
            qs = qs.filter(student_id=student_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)

class VaccinationViewSet(viewsets.ModelViewSet):
    serializer_class = VaccinationSerializer
    permission_classes = [IsApprovedUser, SameSchoolPermission]

    def get_queryset(self):
        qs = Vaccination.objects.filter(school=self.request.user.school)
        student_id = self.request.query_params.get('student_id')
        if student_id:
            qs = qs.filter(student_id=student_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)

class EmergencyMedicalAlertViewSet(viewsets.ModelViewSet):
    serializer_class = EmergencyMedicalAlertSerializer
    permission_classes = [IsApprovedUser, SameSchoolPermission]

    def get_queryset(self):
        qs = EmergencyMedicalAlert.objects.filter(school=self.request.user.school)
        status_param = self.request.query_params.get('status')
        if status_param:
            qs = qs.filter(status=status_param.upper())
        return qs

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, reported_by=self.request.user)

class HealthSummaryView(views.APIView):
    """
    Dashboard metrics for Student Health.
    """
    permission_classes = [IsApprovedUser]

    def get(self, request):
        school = request.user.school
        active_emergencies = EmergencyMedicalAlert.objects.filter(
            school=school,
            status__in=['ACTIVE', 'UNDER_CARE']
        ).count()
        total_students = Student.objects.filter(school=school, is_active=True).count()
        recent_checkups = MedicalCheckup.objects.filter(
            school=school,
            date__gte=timezone.now().date() - timezone.timedelta(days=30)
        ).count()
        students_requiring_attention = EmergencyMedicalAlert.objects.filter(
            school=school,
            severity__in=['HIGH', 'CRITICAL'],
            status__in=['ACTIVE', 'UNDER_CARE']
        ).values('student').distinct().count()

        return Response({
            'active_emergency_cases': active_emergencies,
            'students_requiring_attention': students_requiring_attention,
            'recent_checkups_30d': recent_checkups,
            'total_students': total_students,
        })

class StudentHealthDetailView(views.APIView):
    """
    Get all medical info (profile, checkups, vaccines, alerts) for one student.
    """
    permission_classes = [IsApprovedUser]

    def get(self, request, student_id):
        school = request.user.school
        try:
            student = Student.objects.get(id=student_id, school=school)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found in your school.'}, status=status.HTTP_404_NOT_FOUND)

        health_profile, _ = HealthRecord.objects.get_or_create(
            school=school,
            student=student,
            defaults={'blood_group': student.blood_group}
        )
        checkups = MedicalCheckup.objects.filter(school=school, student=student)
        vaccines = Vaccination.objects.filter(school=school, student=student)
        alerts = EmergencyMedicalAlert.objects.filter(school=school, student=student)

        return Response({
            'student_id': student.id,
            'student_name': student.full_name,
            'health_profile': HealthRecordSerializer(health_profile).data,
            'checkups': MedicalCheckupSerializer(checkups, many=True).data,
            'vaccinations': VaccinationSerializer(vaccines, many=True).data,
            'emergency_alerts': EmergencyMedicalAlertSerializer(alerts, many=True).data
        })
