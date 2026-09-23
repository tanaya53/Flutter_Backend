from rest_framework import serializers
from .models import Scholarship, WelfareScheme

class ScholarshipSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_class = serializers.CharField(source='student.grade_class', read_only=True)
    student_roll = serializers.CharField(source='student.student_id', read_only=True)

    class Meta:
        model = Scholarship
        fields = [
            'id', 'student', 'student_name', 'student_class', 'student_roll',
            'scheme_name', 'application_number', 'amount', 'academic_year',
            'status', 'disbursement_date', 'remarks', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class WelfareSchemeSerializer(serializers.ModelSerializer):
    completion_percentage = serializers.FloatField(read_only=True)

    class Meta:
        model = WelfareScheme
        fields = [
            'id', 'name', 'category', 'target_class', 'total_eligible',
            'total_distributed', 'status', 'distribution_date',
            'completion_percentage', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
