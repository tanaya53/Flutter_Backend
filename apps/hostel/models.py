from django.db import models
from django.conf import settings
from apps.students.models import Student

class Hostel(models.Model):
    BLOCK_TYPES = (
        ('BOYS', 'Boys Hostel Block'),
        ('GIRLS', 'Girls Hostel Block'),
    )

    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        related_name='hostels',
        help_text="Strict school data isolation foreign key"
    )
    name = models.CharField(max_length=150)
    block_type = models.CharField(max_length=20, choices=BLOCK_TYPES, default='BOYS')
    warden = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_hostels'
    )
    total_capacity = models.IntegerField(default=100)

    def __str__(self):
        return f"{self.name} ({self.block_type}) - {self.school.school_id}"

class Room(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=50)
    floor = models.IntegerField(default=1)
    capacity = models.IntegerField(default=6)

    class Meta:
        unique_together = ('hostel', 'room_number')
        ordering = ['floor', 'room_number']

    @property
    def occupied_count(self):
        return self.beds.filter(is_occupied=True).count()

    @property
    def available_count(self):
        return max(0, self.capacity - self.occupied_count)

    def __str__(self):
        return f"Room {self.room_number} ({self.hostel.name})"

class Bed(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='beds')
    bed_number = models.CharField(max_length=50)
    allocated_student = models.OneToOneField(
        Student,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='allocated_bed'
    )
    is_occupied = models.BooleanField(default=False)

    class Meta:
        unique_together = ('room', 'bed_number')

    def __str__(self):
        return f"Bed {self.bed_number} in Room {self.room.room_number}"

class LeaveRequest(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved (On Leave)'),
        ('REJECTED', 'Rejected'),
        ('RETURNED', 'Returned to Hostel'),
    )

    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='leave_requests')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='leaves')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    escort_name = models.CharField(max_length=150, blank=True)
    escort_contact = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Leave: {self.student.full_name} ({self.start_date} to {self.end_date}) [{self.status}]"

class HostelIncident(models.Model):
    TYPE_CHOICES = (
        ('DISCIPLINARY', 'Disciplinary Concern'),
        ('HEALTH', 'Health / Sickness in Dorm'),
        ('MAINTENANCE', 'Facility / Water / Light Issue'),
        ('SECURITY', 'Hostel Security / Boundary Concern'),
        ('OTHER', 'Other Incident'),
    )

    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='hostel_incidents')
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True, related_name='hostel_incidents')
    incident_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='DISCIPLINARY')
    title = models.CharField(max_length=200)
    description = models.TextField()
    action_taken = models.TextField(blank=True)
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Incident: {self.title} ({self.incident_type})"

class Meal(models.Model):
    MEAL_TYPES = (
        ('BREAKFAST', 'Breakfast (सकाळचा नाश्ता)'),
        ('LUNCH', 'Lunch (दुपारचे जेवण)'),
        ('SNACK', 'Evening Snack (संध्याकाळचा नाश्ता)'),
        ('DINNER', 'Dinner (रात्रीचे जेवण)'),
    )

    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='meal_records')
    date = models.DateField()
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES)
    menu_description = models.TextField(help_text="Items served: e.g., Dal, Rice, Chapati, Matki Usal, Milk")
    students_served = models.IntegerField(default=0)
    quality_status = models.CharField(max_length=50, default='Good / Inspected')
    inspected_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', 'meal_type']
        unique_together = ('school', 'date', 'meal_type')

    def __str__(self):
        return f"{self.date} {self.meal_type} - {self.students_served} served"

class FoodStock(models.Model):
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='food_stocks')
    item_name = models.CharField(max_length=150)
    quantity = models.FloatField(default=0.0)
    unit = models.CharField(max_length=30, default='kg')
    low_stock_threshold = models.FloatField(default=25.0)
    last_replenished = models.DateField(auto_now=True)

    class Meta:
        ordering = ['item_name']

    @property
    def is_low_stock(self):
        return self.quantity <= self.low_stock_threshold

    def __str__(self):
        return f"{self.item_name}: {self.quantity} {self.unit}"
