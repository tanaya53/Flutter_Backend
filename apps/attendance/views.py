from rest_framework import viewsets, views, status
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta
from .models import DailyAttendance, HostelAttendance
from .serializers import (
    DailyAttendanceSerializer,
    BulkDailyAttendanceSerializer,
    HostelAttendanceSerializer
)
from apps.students.models import Student
from apps.accounts.permissions import IsApprovedUser, SameSchoolPermission

class DailyAttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = DailyAttendanceSerializer
    permission_classes = [IsApprovedUser, SameSchoolPermission]

    def get_queryset(self):
        user = self.request.user
        qs = DailyAttendance.objects.filter(school=user.school)
        
        target_date = self.request.query_params.get('date')
        if target_date:
            qs = qs.filter(date=target_date)
            
        grade_class = self.request.query_params.get('grade_class')
        if grade_class:
            qs = qs.filter(student__grade_class__iexact=grade_class)

        status_param = self.request.query_params.get('status')
        if status_param:
            qs = qs.filter(status=status_param.upper())

        return qs

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, marked_by=self.request.user)

class BulkAttendanceView(views.APIView):
    """
    Allows teachers or wardens to submit attendance records for multiple students in one call.
    Also used by Flutter offline synchronization engine.
    """
    permission_classes = [IsApprovedUser]

    def post(self, request):
        serializer = BulkDailyAttendanceSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        target_date = data['date']
        attendances = data['attendances']
        school = request.user.school

        records_updated = 0
        for item in attendances:
            try:
                student = Student.objects.get(id=item['student_id'], school=school)
                DailyAttendance.objects.update_or_create(
                    school=school,
                    student=student,
                    date=target_date,
                    defaults={
                        'status': item['status'],
                        'remarks': item.get('remarks', ''),
                        'marked_by': request.user
                    }
                )
                records_updated += 1
            except Student.DoesNotExist:
                continue

        return Response({
            'message': f'Successfully recorded attendance for {records_updated} students.',
            'date': target_date,
            'count': records_updated
        }, status=status.HTTP_200_OK)

class StudentAttendanceHistoryView(views.APIView):
    """
    Retrieves full attendance history for a single student.
    Guaranteed school isolation.
    """
    permission_classes = [IsApprovedUser]

    def get(self, request, student_id):
        school = request.user.school
        try:
            student = Student.objects.get(id=student_id, school=school)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found in your school.'}, status=status.HTTP_404_NOT_FOUND)

        records = DailyAttendance.objects.filter(school=school, student=student).order_by('-date')
        total = records.count()
        present = records.filter(status='PRESENT').count()
        rate = round((present / total * 100), 1) if total > 0 else 100.0

        return Response({
            'student_id': student.id,
            'student_name': student.full_name,
            'total_days': total,
            'present_days': present,
            'absent_days': records.filter(status='ABSENT').count(),
            'leave_days': records.filter(status='ON_LEAVE').count(),
            'attendance_rate': rate,
            'history': DailyAttendanceSerializer(records[:60], many=True).data
        })

class RepeatedAbsenteesView(views.APIView):
    """
    Safety feature: Detects students with 3 or more absences in the past 14 days.
    """
    permission_classes = [IsApprovedUser]

    def get(self, request):
        school = request.user.school
        cutoff_date = timezone.now().date() - timedelta(days=14)

        absent_counts = (
            DailyAttendance.objects.filter(
                school=school,
                status='ABSENT',
                date__gte=cutoff_date
            )
            .values('student_id', 'student__first_name', 'student__last_name', 'student__grade_class', 'student__student_id')
            .annotate(absent_count=Count('id'))
            .filter(absent_count__gte=3)
            .order_by('-absent_count')
        )

        results = [
            {
                'student_id': row['student_id'],
                'student_name': f"{row['student__first_name']} {row['student__last_name']}".strip(),
                'student_code': row['student__student_id'],
                'grade_class': row['student__grade_class'],
                'absent_days': row['absent_count'],
                'risk_level': 'HIGH' if row['absent_count'] >= 5 else 'MODERATE',
                'alert': f"Repeated Absence Alert: {row['absent_count']} days missed in the last 2 weeks."
            }
            for row in absent_counts
        ]

        return Response(results)

class AttendanceSummaryView(views.APIView):
    """
    Dashboard metric endpoint for Today's Attendance.
    """
    permission_classes = [IsApprovedUser]

    def get(self, request):
        school = request.user.school
        today = timezone.now().date()
        date_str = request.query_params.get('date', str(today))

        total_students = Student.objects.filter(school=school, is_active=True).count()
        today_records = DailyAttendance.objects.filter(school=school, date=date_str)

        present = today_records.filter(status='PRESENT').count()
        absent = today_records.filter(status='ABSENT').count()
        on_leave = today_records.filter(status='ON_LEAVE').count()
        unmarked = max(0, total_students - (present + absent + on_leave))
        percentage = round((present / total_students * 100), 1) if total_students > 0 else 0.0

        return Response({
            'date': date_str,
            'total_students': total_students,
            'present': present,
            'absent': absent,
            'on_leave': on_leave,
            'unmarked': unmarked,
            'attendance_percentage': percentage
        })

class HostelAttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = HostelAttendanceSerializer
    permission_classes = [IsApprovedUser, SameSchoolPermission]

    def get_queryset(self):
        user = self.request.user
        qs = HostelAttendance.objects.filter(school=user.school)
        date_val = self.request.query_params.get('date')
        if date_val:
            qs = qs.filter(date=date_val)
        return qs

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, marked_by=self.request.user)
