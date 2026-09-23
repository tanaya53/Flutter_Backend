from django.db import models
from django.conf import settings

class InventoryItem(models.Model):
    CATEGORY_CHOICES = (
        ('BEDDING', 'Hostel Bedding & Cots'),
        ('UNIFORM', 'School Uniforms & Shoes'),
        ('BOOK', 'Library Books & Textbooks'),
        ('SPORTS', 'Sports & Physical Ed Equipment'),
        ('LAB', 'Science & ICT Lab Resources'),
        ('COMPUTER', 'Computers & Digital Tools'),
        ('HOSTEL_SUPPLY', 'Hostel & Sanitation Supplies'),
        ('GENERAL', 'General Institutional Assets'),
    )

    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        related_name='inventory_items',
        help_text="Strict school data isolation foreign key"
    )
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='GENERAL')
    total_quantity = models.IntegerField(default=0)
    allocated_quantity = models.IntegerField(default=0)
    unit = models.CharField(max_length=50, default='Units')
    low_stock_threshold = models.IntegerField(default=10)
    storage_location = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'name']

    @property
    def available_quantity(self):
        return max(0, self.total_quantity - self.allocated_quantity)

    @property
    def is_low_stock(self):
        return self.available_quantity <= self.low_stock_threshold

    def __str__(self):
        return f"{self.name} ({self.available_quantity}/{self.total_quantity} {self.unit})"

class InventoryTransaction(models.Model):
    TXN_TYPES = (
        ('STOCK_IN', 'Stock Added / Procured'),
        ('ISSUE', 'Issued to Student / Staff'),
        ('RETURN', 'Returned to Inventory'),
        ('DAMAGED', 'Marked Damaged / Written-off'),
    )

    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='inventory_transactions')
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TXN_TYPES, default='STOCK_IN')
    quantity = models.IntegerField()
    recipient_name = models.CharField(max_length=150, blank=True)
    recipient_role = models.CharField(max_length=50, blank=True)
    handled_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    remarks = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.transaction_type} - {self.quantity} x {self.item.name}"
