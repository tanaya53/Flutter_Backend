from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('principal', 'Principal / Admin'),
        ('teacher', 'Teacher / Mentor'),
        ('warden', 'Hostel Warden'),
        ('parent', 'Parent / Guardian'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='teacher')
    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='users',
        help_text="The school this user strictly belongs to"
    )
    phone_number = models.CharField(max_length=20, blank=True)
    is_approved = models.BooleanField(
        default=False,
        help_text="Requires Principal approval before granting access (Principals are auto-approved)"
    )

    class Meta:
        indexes = [
            models.Index(fields=['school', 'role']),
            models.Index(fields=['username']),
        ]

    def __str__(self):
        school_str = self.school.school_id if self.school else 'No School'
        return f"{self.get_full_name() or self.username} ({self.role} - {school_str})"

class SchoolJoinRequest(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='join_requests')
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='join_requests')
    requested_role = models.CharField(max_length=20, choices=User.ROLE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    request_date = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_requests'
    )
    approval_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-request_date']
        indexes = [
            models.Index(fields=['school', 'status']),
        ]

    def __str__(self):
        return f"JoinRequest: {self.user.username} for {self.school.school_id} ({self.status})"

class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='teachers')
    qualification = models.CharField(max_length=100, blank=True)
    specialization = models.CharField(max_length=100, blank=True)
    joining_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Teacher: {self.user.get_full_name() or self.user.username}"

class WardenProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='warden_profile')
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='wardens')
    assigned_block = models.CharField(max_length=100, blank=True)
    contact_ext = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"Warden: {self.user.get_full_name() or self.user.username}"
