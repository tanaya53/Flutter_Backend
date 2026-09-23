from rest_framework import serializers
from .models import Hostel, Room, Bed, LeaveRequest, HostelIncident, Meal, FoodStock

class BedSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='allocated_student.full_name', read_only=True)
    student_roll = serializers.CharField(source='allocated_student.student_id', read_only=True)

    class Meta:
        model = Bed
        fields = ['id', 'room', 'bed_number', 'allocated_student', 'student_name', 'student_roll', 'is_occupied']

class RoomSerializer(serializers.ModelSerializer):
    beds = BedSerializer(many=True, read_only=True)
    occupied_count = serializers.IntegerField(read_only=True)
    available_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'hostel', 'room_number', 'floor', 'capacity', 'occupied_count', 'available_count', 'beds']

class HostelSerializer(serializers.ModelSerializer):
    warden_name = serializers.CharField(source='warden.get_full_name', read_only=True)
    rooms = RoomSerializer(many=True, read_only=True)
    total_beds = serializers.SerializerMethodField()
    occupied_beds = serializers.SerializerMethodField()

    class Meta:
        model = Hostel
        fields = ['id', 'name', 'block_type', 'warden', 'warden_name', 'total_capacity', 'total_beds', 'occupied_beds', 'rooms']

    def get_total_beds(self, obj):
        return Bed.objects.filter(room__hostel=obj).count()

    def get_occupied_beds(self, obj):
        return Bed.objects.filter(room__hostel=obj, is_occupied=True).count()

class LeaveRequestSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_class = serializers.CharField(source='student.grade_class', read_only=True)

    class Meta:
        model = LeaveRequest
        fields = [
            'id', 'student', 'student_name', 'student_class', 'start_date',
            'end_date', 'reason', 'escort_name', 'escort_contact', 'status',
            'approved_by', 'created_at'
        ]
        read_only_fields = ['id', 'approved_by', 'created_at']

class HostelIncidentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    reported_by_name = serializers.CharField(source='reported_by.get_full_name', read_only=True)

    class Meta:
        model = HostelIncident
        fields = [
            'id', 'student', 'student_name', 'incident_type', 'title',
            'description', 'action_taken', 'reported_by', 'reported_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'reported_by', 'created_at']

class MealSerializer(serializers.ModelSerializer):
    inspected_by_name = serializers.CharField(source='inspected_by.get_full_name', read_only=True)

    class Meta:
        model = Meal
        fields = [
            'id', 'date', 'meal_type', 'menu_description', 'students_served',
            'quality_status', 'inspected_by', 'inspected_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'inspected_by', 'created_at']

class FoodStockSerializer(serializers.ModelSerializer):
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = FoodStock
        fields = ['id', 'item_name', 'quantity', 'unit', 'low_stock_threshold', 'is_low_stock', 'last_replenished']
        read_only_fields = ['id', 'last_replenished']
