from django.db import models

class School(models.Model):
    SCHOOL_TYPES = (
        ('GOVT_ASHRAM', 'Government Ashram School'),
        ('EMRS', 'Eklavya Model Residential School'),
        ('TRIBAL_RESIDENTIAL', 'Tribal Residential School'),
        ('AIDED_ASHRAM', 'Aided Ashram School'),
    )

    school_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Unique institutional school identifier (e.g. ASH001)"
    )
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100, default='Maharashtra')
    school_type = models.CharField(max_length=50, choices=SCHOOL_TYPES, default='GOVT_ASHRAM')
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['school_id']),
        ]

    def __str__(self):
        return f"{self.name} ({self.school_id})"
