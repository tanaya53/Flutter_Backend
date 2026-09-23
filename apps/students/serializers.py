from rest_framework import serializers
from .models import Student, Guardian, AcademicRemark, StudentConcern
from apps.accounts.serializers import UserSerializer

class GuardianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guardian
        fields = ['id', 'name', 'relationship', 'contact_number', 'occupation', 'address']

class StudentSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    assigned_mentor_name = serializers.CharField(source='assigned_mentor.get_full_name', read_only=True)
    guardians = GuardianSerializer(many=True, read_only=True)

    class Meta:
        model = Student
        fields = [
            'id', 'student_id', 'first_name', 'last_name', 'full_name',
            'photo_url', 'dob', 'gender', 'grade_class', 'division',
            'admission_number', 'admission_date', 'address', 'emergency_contact',
            'blood_group', 'assigned_mentor', 'assigned_mentor_name',
            'hostel_block', 'room_number', 'bed_number', 'is_active',
            'guardians', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class AcademicRemarkSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    student_name = serializers.CharField(source='student.full_name', read_only=True)

    class Meta:
        model = AcademicRemark
        fields = [
            'id', 'student', 'student_name', 'teacher', 'teacher_name',
            'subject', 'term', 'remark', 'performance', 'date'
        ]
        read_only_fields = ['id', 'teacher', 'date']

class StudentConcernSerializer(serializers.ModelSerializer):
    reported_by_name = serializers.CharField(source='reported_by.get_full_name', read_only=True)
    student_name = serializers.CharField(source='student.full_name', read_only=True)

    class Meta:
        model = StudentConcern
        fields = [
            'id', 'student', 'student_name', 'reported_by', 'reported_by_name',
            'category', 'description', 'severity', 'status', 'resolution_notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'reported_by', 'created_at', 'updated_at']
