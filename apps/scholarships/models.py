from django.db import models
from apps.students.models import Student

class Scholarship(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Application Pending'),
        ('SUBMITTED', 'Submitted to Dept'),
        ('UNDER_REVIEW', 'Under Review / Scrutiny'),
        ('APPROVED', 'Approved by Tribal Dept'),
        ('REJECTED', 'Rejected'),
        ('DISTRIBUTED', 'Amount Disbursed / Distributed'),
    )

    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        related_name='scholarships',
        help_text="Strict school data isolation foreign key"
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='scholarships')
    scheme_name = models.CharField(max_length=200)
    application_number = models.CharField(max_length=100, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    academic_year = models.CharField(max_length=20, default='2026-2027')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PENDING')
    disbursement_date = models.DateField(null=True, blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.scheme_name} - {self.student.full_name} ({self.status})"

class WelfareScheme(models.Model):
    CATEGORY_CHOICES = (
        ('UNIFORM', 'School Uniforms Distribution'),
        ('TEXTBOOKS', 'Government Free Textbooks'),
        ('STATIONERY', 'Notebooks & Educational Kit'),
        ('HOSTEL_KIT', 'Hostel Bedding & Personal Care Kit'),
        ('FOOD_BENEFIT', 'Direct Nutritional Support Scheme'),
        ('OTHER', 'General Tribal Welfare Scheme'),
    )
    STATUS_CHOICES = (
        ('PLANNED', 'Planned'),
        ('IN_PROGRESS', 'Distribution in Progress'),
        ('COMPLETED', 'Fully Distributed'),
    )

    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='welfare_schemes')
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='UNIFORM')
    target_class = models.CharField(max_length=100, default='All Ashram Students')
    total_eligible = models.IntegerField(default=0)
    total_distributed = models.IntegerField(default=0)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='IN_PROGRESS')
    distribution_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def completion_percentage(self):
        return round((self.total_distributed / self.total_eligible * 100), 1) if self.total_eligible > 0 else 0.0

    def __str__(self):
        return f"{self.name} ({self.status}) - {self.school.school_id}"
