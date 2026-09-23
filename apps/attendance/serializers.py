from rest_framework import serializers
from .models import DailyAttendance, HostelAttendance
from apps.students.models import Student

class DailyAttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_roll = serializers.CharField(source='student.student_id', read_only=True)
    grade_class = serializers.CharField(source='student.grade_class', read_only=True)

    class Meta:
        model = DailyAttendance
        fields = [
            'id', 'student', 'student_name', 'student_roll', 'grade_class',
            'date', 'status', 'remarks', 'marked_by', 'created_at'
        ]
        read_only_fields = ['id', 'marked_by', 'created_at']

class BulkAttendanceItemSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    status = serializers.ChoiceField(choices=['PRESENT', 'ABSENT', 'ON_LEAVE'])
    remarks = serializers.CharField(required=False, allow_blank=True, default='')

class BulkDailyAttendanceSerializer(serializers.Serializer):
    date = serializers.DateField()
    attendances = BulkAttendanceItemSerializer(many=True)

class HostelAttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    room_number = serializers.CharField(source='student.room_number', read_only=True)
    bed_number = serializers.CharField(source='student.bed_number', read_only=True)

    class Meta:
        model = HostelAttendance
        fields = [
            'id', 'student', 'student_name', 'room_number', 'bed_number',
            'date', 'session', 'status', 'remarks', 'marked_by', 'created_at'
        ]
        read_only_fields = ['id', 'marked_by', 'created_at']
