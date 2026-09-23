from rest_framework import viewsets, views, status, permissions
from rest_framework.response import Response
from django.utils import timezone
from .models import Hostel, Room, Bed, LeaveRequest, HostelIncident, Meal, FoodStock
from .serializers import (
    HostelSerializer,
    RoomSerializer,
    BedSerializer,
    LeaveRequestSerializer,
    HostelIncidentSerializer,
    MealSerializer,
    FoodStockSerializer
)
from apps.accounts.permissions import IsApprovedUser, SameSchoolPermission
from apps.students.models import Student

class HostelViewSet(viewsets.ModelViewSet):
    serializer_class = HostelSerializer
    permission_classes = [IsApprovedUser, SameSchoolPermission]

    def get_queryset(self):
        return Hostel.objects.filter(school=self.request.user.school).prefetch_related('rooms__beds')

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)

class RoomViewSet(viewsets.ModelViewSet):
    serializer_class = RoomSerializer
    permission_classes = [IsApprovedUser]

    def get_queryset(self):
        return Room.objects.filter(hostel__school=self.request.user.school).prefetch_related('beds')

class AllocateBedView(views.APIView):
    """
    Allocates or de-allocates a student to a specific bed.
    """
    permission_classes = [IsApprovedUser]

    def post(self, request):
        student_id = request.data.get('student_id')
        bed_id = request.data.get('bed_id')
        action = request.data.get('action', 'ALLOCATE').upper()
        school = request.user.school

        try:
            bed = Bed.objects.get(id=bed_id, room__hostel__school=school)
        except Bed.DoesNotExist:
            return Response({'error': 'Bed not found in your school.'}, status=status.HTTP_404_NOT_FOUND)

        if action == 'DEALLOCATE':
            if bed.allocated_student:
                stud = bed.allocated_student
                stud.hostel_block = ''
                stud.room_number = ''
                stud.bed_number = ''
                stud.save()
            bed.allocated_student = None
            bed.is_occupied = False
            bed.save()
            return Response({'message': 'Bed deallocated successfully'})

        try:
            student = Student.objects.get(id=student_id, school=school)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found in your school.'}, status=status.HTTP_404_NOT_FOUND)

        # Clear any prior bed student had
        Bed.objects.filter(allocated_student=student).update(allocated_student=None, is_occupied=False)

        bed.allocated_student = student
        bed.is_occupied = True
        bed.save()

        student.hostel_block = bed.room.hostel.name
        student.room_number = bed.room.room_number
        student.bed_number = bed.bed_number
        student.save()

        return Response({
            'message': f"Student {student.full_name} allocated to Room {bed.room.room_number} Bed {bed.bed_number}",
            'bed': BedSerializer(bed).data
        })

class LeaveRequestViewSet(viewsets.ModelViewSet):
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsApprovedUser, SameSchoolPermission]

    def get_queryset(self):
        return LeaveRequest.objects.filter(school=self.request.user.school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)

class ProcessLeaveView(views.APIView):
    """
    Warden or Principal approves, rejects, or marks student returned.
    """
    permission_classes = [IsApprovedUser]

    def post(self, request, pk):
        try:
            leave = LeaveRequest.objects.get(pk=pk, school=request.user.school)
        except LeaveRequest.DoesNotExist:
            return Response({'error': 'Leave request not found.'}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get('status', '').upper()
        if action not in ['APPROVED', 'REJECTED', 'RETURNED']:
            return Response({'error': "Status must be 'APPROVED', 'REJECTED', or 'RETURNED'"}, status=status.HTTP_400_BAD_REQUEST)

        leave.status = action
        leave.approved_by = request.user
        leave.save()

        return Response({
            'message': f'Leave marked as {action}',
            'leave': LeaveRequestSerializer(leave).data
        })

class HostelIncidentViewSet(viewsets.ModelViewSet):
    serializer_class = HostelIncidentSerializer
    permission_classes = [IsApprovedUser, SameSchoolPermission]

    def get_queryset(self):
        return HostelIncident.objects.filter(school=self.request.user.school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, reported_by=self.request.user)

class MealViewSet(viewsets.ModelViewSet):
    serializer_class = MealSerializer
    permission_classes = [IsApprovedUser, SameSchoolPermission]

    def get_queryset(self):
        qs = Meal.objects.filter(school=self.request.user.school)
        date_param = self.request.query_params.get('date')
        if date_param:
            qs = qs.filter(date=date_param)
        return qs

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, inspected_by=self.request.user)

class FoodStockViewSet(viewsets.ModelViewSet):
    serializer_class = FoodStockSerializer
    permission_classes = [IsApprovedUser, SameSchoolPermission]

    def get_queryset(self):
        return FoodStock.objects.filter(school=self.request.user.school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)

class HostelSummaryView(views.APIView):
    """
    Hostel and Nutrition dashboard metrics.
    """
    permission_classes = [IsApprovedUser]

    def get(self, request):
        school = request.user.school
        total_beds = Bed.objects.filter(room__hostel__school=school).count()
        occupied_beds = Bed.objects.filter(room__hostel__school=school, is_occupied=True).count()
        available_beds = max(0, total_beds - occupied_beds)
        occupancy_rate = round((occupied_beds / total_beds * 100), 1) if total_beds > 0 else 0.0

        pending_leaves = LeaveRequest.objects.filter(school=school, status='PENDING').count()
        active_leaves = LeaveRequest.objects.filter(school=school, status='APPROVED').count()
        low_food_stocks = [stock.item_name for stock in FoodStock.objects.filter(school=school) if stock.is_low_stock]

        return Response({
            'total_beds': total_beds,
            'occupied_beds': occupied_beds,
            'available_beds': available_beds,
            'occupancy_percentage': occupancy_rate,
            'pending_leave_requests': pending_leaves,
            'students_on_leave': active_leaves,
            'low_food_stocks_count': len(low_food_stocks),
            'low_food_stocks_items': low_food_stocks,
        })
