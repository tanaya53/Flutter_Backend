from rest_framework import serializers
from .models import HealthRecord, MedicalCheckup, Vaccination, EmergencyMedicalAlert

class HealthRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_class = serializers.CharField(source='student.grade_class', read_only=True)

    class Meta:
        model = HealthRecord
        fields = [
            'id', 'student', 'student_name', 'student_class', 'blood_group',
            'allergies', 'chronic_conditions', 'height_cm', 'weight_kg',
            'last_checkup_date', 'emergency_medical_notes', 'updated_at'
        ]
        read_only_fields = ['id', 'updated_at']

class MedicalCheckupSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)

    class Meta:
        model = MedicalCheckup
        fields = [
            'id', 'student', 'student_name', 'date', 'doctor_name',
            'findings', 'prescriptions', 'next_checkup_date', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class VaccinationSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)

    class Meta:
        model = Vaccination
        fields = [
            'id', 'student', 'student_name', 'vaccine_name', 'dosage',
            'administered_date', 'administered_by'
        ]
        read_only_fields = ['id']

class EmergencyMedicalAlertSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_class = serializers.CharField(source='student.grade_class', read_only=True)
    reported_by_name = serializers.CharField(source='reported_by.get_full_name', read_only=True)

    class Meta:
        model = EmergencyMedicalAlert
        fields = [
            'id', 'student', 'student_name', 'student_class', 'title',
            'description', 'severity', 'status', 'hospital_admitted',
            'hospital_name', 'doctor_contact', 'reported_by', 'reported_by_name',
            'reported_at', 'resolved_at'
        ]
        read_only_fields = ['id', 'reported_by', 'reported_at']
