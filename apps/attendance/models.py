from django.db import models
from django.conf import settings
from apps.students.models import Student

class DailyAttendance(models.Model):
    STATUS_CHOICES = (
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('ON_LEAVE', 'On Leave'),
    )

    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        related_name='daily_attendances',
        help_text="Strict school data isolation foreign key"
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PRESENT')
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='marked_attendances'
    )
    remarks = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('school', 'student', 'date')
        ordering = ['-date', 'student__first_name']
        indexes = [
            models.Index(fields=['school', 'date', 'status']),
            models.Index(fields=['school', 'student', 'date']),
        ]

    def __str__(self):
        return f"{self.student.full_name} - {self.date} - {self.status}"

class HostelAttendance(models.Model):
    SESSION_CHOICES = (
        ('MORNING', 'Morning Roll Call'),
        ('NIGHT', 'Night Roll Call'),
    )
    STATUS_CHOICES = (
        ('PRESENT', 'Present in Hostel'),
        ('ABSENT', 'Unaccounted / Absent'),
        ('ON_LEAVE', 'Official Leave'),
    )

    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='hostel_attendances')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='hostel_attendances')
    date = models.DateField(db_index=True)
    session = models.CharField(max_length=20, choices=SESSION_CHOICES, default='NIGHT')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PRESENT')
    marked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    remarks = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('school', 'student', 'date', 'session')
        ordering = ['-date', 'student__first_name']
        indexes = [
            models.Index(fields=['school', 'date', 'session']),
        ]

    def __str__(self):
        return f"Hostel {self.session} - {self.student.full_name} - {self.date} ({self.status})"
