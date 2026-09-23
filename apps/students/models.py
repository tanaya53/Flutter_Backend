from django.db import models
from django.conf import settings

class Student(models.Model):
    GENDER_CHOICES = (
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other'),
    )

    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        related_name='students',
        help_text="Strict school data isolation foreign key"
    )
    student_id = models.CharField(max_length=50, help_text="Unique student roll/registration number within school")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    photo_url = models.CharField(max_length=500, blank=True, default='')
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='MALE')
    grade_class = models.CharField(max_length=50, help_text="e.g. Class 6, Class 7")
    division = models.CharField(max_length=10, default='A')
    admission_number = models.CharField(max_length=50, blank=True)
    admission_date = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=20, blank=True)
    blood_group = models.CharField(max_length=10, blank=True, default='O+')
    
    # Mentor and Hostel allocation
    assigned_mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mentored_students',
        help_text="Assigned Teacher/Mentor"
    )
    hostel_block = models.CharField(max_length=100, blank=True, default='')
    room_number = models.CharField(max_length=50, blank=True, default='')
    bed_number = models.CharField(max_length=50, blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['grade_class', 'division', 'first_name']
        unique_together = ('school', 'student_id')
        indexes = [
            models.Index(fields=['school', 'student_id']),
            models.Index(fields=['school', 'grade_class']),
            models.Index(fields=['school', 'assigned_mentor']),
        ]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return f"{self.full_name} ({self.student_id}) - {self.school.school_id}"

class Guardian(models.Model):
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='guardians')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='guardians')
    name = models.CharField(max_length=150)
    relationship = models.CharField(max_length=50, default='Parent')
    contact_number = models.CharField(max_length=20)
    occupation = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='linked_wards',
        help_text="Parent user account if registered"
    )

    def __str__(self):
        return f"{self.name} ({self.relationship} of {self.student.full_name})"

class AcademicRemark(models.Model):
    PERFORMANCE_CHOICES = (
        ('EXCELLENT', 'Excellent'),
        ('GOOD', 'Good'),
        ('AVERAGE', 'Average'),
        ('NEEDS_IMPROVEMENT', 'Needs Improvement'),
    )

    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='academic_remarks')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='academic_remarks')
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='remarks_given')
    subject = models.CharField(max_length=100)
    term = models.CharField(max_length=50, default='Unit Test 1')
    remark = models.TextField()
    performance = models.CharField(max_length=30, choices=PERFORMANCE_CHOICES, default='GOOD')
    date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Remark for {self.student.full_name} by {self.teacher.username}"

class StudentConcern(models.Model):
    CATEGORY_CHOICES = (
        ('ACADEMIC', 'Academic Issue'),
        ('HEALTH', 'Health / Medical'),
        ('HOMESICKNESS', 'Homesickness / Emotional'),
        ('BEHAVIORAL', 'Behavioral / Discipline'),
        ('FINANCIAL', 'Welfare / Financial'),
    )
    SEVERITY_CHOICES = (
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical / Emergency'),
    )
    STATUS_CHOICES = (
        ('OPEN', 'Open'),
        ('UNDER_REVIEW', 'Under Review'),
        ('RESOLVED', 'Resolved'),
    )

    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='student_concerns')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='concerns')
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reported_concerns')
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='ACADEMIC')
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='MEDIUM')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    resolution_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Concern [{self.severity}]: {self.student.full_name} ({self.category})"
