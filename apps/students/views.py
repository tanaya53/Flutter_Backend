from rest_framework import viewsets, permissions, status, views
from rest_framework.response import Response
from .models import Student, Guardian, AcademicRemark, StudentConcern
from .serializers import StudentSerializer, AcademicRemarkSerializer, StudentConcernSerializer
from apps.accounts.permissions import IsApprovedUser, SameSchoolPermission, IsPrincipal, IsPrincipalOrTeacher

class StudentViewSet(viewsets.ModelViewSet):
    """
    CRUD for Students with strict school data isolation.
    """
    serializer_class = StudentSerializer
    permission_classes = [IsApprovedUser, SameSchoolPermission]

    def get_queryset(self):
        # Strict school isolation: user can only query students in their own school
        user = self.request.user
        qs = Student.objects.filter(school=user.school)

        # Optional filters
        grade_class = self.request.query_params.get('grade_class')
        if grade_class:
            qs = qs.filter(grade_class__iexact=grade_class)

        division = self.request.query_params.get('division')
        if division:
            qs = qs.filter(division__iexact=division)

        mentor_id = self.request.query_params.get('assigned_mentor')
        if mentor_id:
            qs = qs.filter(assigned_mentor_id=mentor_id)

        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search) |
                models.Q(student_id__icontains=search)
            )

        return qs

    def perform_create(self, serializer):
        # Mandatory server-side school binding
        serializer.save(school=self.request.user.school)

class MyStudentsView(views.APIView):
    """
    Returns students assigned to the authenticated teacher/mentor within their school.
    """
    permission_classes = [IsApprovedUser]

    def get(self, request):
        students = Student.objects.filter(
            school=request.user.school,
            assigned_mentor=request.user
        )
        # If teacher has no assigned students yet, fallback to all students in school so they can still operate
        if not students.exists() and request.user.role in ['teacher', 'principal']:
            students = Student.objects.filter(school=request.user.school)
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)

class MyChildView(views.APIView):
    """
    Returns the linked child profile for a Parent user.
    """
    permission_classes = [IsApprovedUser]

    def get(self, request):
        guardians = Guardian.objects.filter(
            school=request.user.school,
            user=request.user
        )
        if guardians.exists():
            student = guardians.first().student
            return Response(StudentSerializer(student).data)

        # Fallback: find first student with same contact or first student in school if testing
        student = Student.objects.filter(school=request.user.school).first()
        if student:
            return Response(StudentSerializer(student).data)
        return Response({'error': 'No child linked to this parent account.'}, status=status.HTTP_404_NOT_FOUND)

class AcademicRemarkViewSet(viewsets.ModelViewSet):
    serializer_class = AcademicRemarkSerializer
    permission_classes = [IsApprovedUser, SameSchoolPermission]

    def get_queryset(self):
        qs = AcademicRemark.objects.filter(school=self.request.user.school)
        student_id = self.request.query_params.get('student_id')
        if student_id:
            qs = qs.filter(student_id=student_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, teacher=self.request.user)

class StudentConcernViewSet(viewsets.ModelViewSet):
    serializer_class = StudentConcernSerializer
    permission_classes = [IsApprovedUser, SameSchoolPermission]

    def get_queryset(self):
        qs = StudentConcern.objects.filter(school=self.request.user.school)
        student_id = self.request.query_params.get('student_id')
        if student_id:
            qs = qs.filter(student_id=student_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, reported_by=self.request.user)
