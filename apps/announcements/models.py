from django.db import models
from django.conf import settings

class Announcement(models.Model):
    TARGET_ROLES = (
        ('ALL', 'Entire Ashram School Community'),
        ('TEACHERS', 'Teachers / Mentors Only'),
        ('WARDENS', 'Hostel Wardens Only'),
        ('PARENTS', 'Parents & Guardians Only'),
    )

    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        related_name='announcements',
        help_text="Strict school data isolation foreign key"
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    target_role = models.CharField(max_length=30, choices=TARGET_ROLES, default='ALL')
    target_class = models.CharField(max_length=50, blank=True, default='All')
    is_emergency = models.BooleanField(default=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_emergency', '-created_at']

    def __str__(self):
        alert_tag = "[EMERGENCY] " if self.is_emergency else ""
        return f"{alert_tag}{self.title} ({self.school.school_id})"

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='notifications')
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-announcement__created_at']

    def __str__(self):
        return f"Notification for {self.user.username} - Read: {self.is_read}"
