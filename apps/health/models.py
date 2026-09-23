from django.db import models
from django.conf import settings
from apps.students.models import Student

class HealthRecord(models.Model):
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='health_records')
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='health_profile')
    blood_group = models.CharField(max_length=10, default='O+')
    allergies = models.TextField(blank=True, default='None known')
    chronic_conditions = models.TextField(blank=True, default='None')
    height_cm = models.FloatField(null=True, blank=True)
    weight_kg = models.FloatField(null=True, blank=True)
    last_checkup_date = models.DateField(null=True, blank=True)
    emergency_medical_notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Health Profile: {self.student.full_name} ({self.blood_group})"

class MedicalCheckup(models.Model):
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='medical_checkups')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='medical_checkups')
    date = models.DateField()
    doctor_name = models.CharField(max_length=150)
    findings = models.TextField()
    prescriptions = models.TextField(blank=True)
    next_checkup_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Checkup: {self.student.full_name} on {self.date}"

class Vaccination(models.Model):
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='vaccinations')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='vaccinations')
    vaccine_name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=50, default='1st Dose')
    administered_date = models.DateField()
    administered_by = models.CharField(max_length=150, blank=True)

    class Meta:
        ordering = ['-administered_date']

    def __str__(self):
        return f"{self.vaccine_name} - {self.student.full_name}"

class EmergencyMedicalAlert(models.Model):
    SEVERITY_CHOICES = (
        ('LOW', 'Low Attention'),
        ('MEDIUM', 'Moderate Concern'),
        ('HIGH', 'High Urgency'),
        ('CRITICAL', 'Critical Emergency'),
    )
    STATUS_CHOICES = (
        ('ACTIVE', 'Active Alert'),
        ('UNDER_CARE', 'Under Medical Care'),
        ('RESOLVED', 'Resolved'),
    )

    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='emergency_health_alerts')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='emergency_alerts')
    title = models.CharField(max_length=200)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='HIGH')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    hospital_admitted = models.BooleanField(default=False)
    hospital_name = models.CharField(max_length=200, blank=True)
    doctor_contact = models.CharField(max_length=50, blank=True)
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reported_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-reported_at']

    def __str__(self):
        return f"ALERT [{self.severity}]: {self.student.full_name} - {self.title}"
