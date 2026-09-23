from rest_framework import viewsets, views, status, permissions
from rest_framework.response import Response
from django.db import transaction
from .models import InventoryItem, InventoryTransaction
from .serializers import InventoryItemSerializer, InventoryTransactionSerializer
from apps.accounts.permissions import IsApprovedUser, SameSchoolPermission

class InventoryItemViewSet(viewsets.ModelViewSet):
    serializer_class = InventoryItemSerializer
    permission_classes = [IsApprovedUser, SameSchoolPermission]

    def get_queryset(self):
        qs = InventoryItem.objects.filter(school=self.request.user.school)
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category=category.upper())
        return qs

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)

class InventoryTransactionViewSet(viewsets.ModelViewSet):
    serializer_class = InventoryTransactionSerializer
    permission_classes = [IsApprovedUser, SameSchoolPermission]

    def get_queryset(self):
        return InventoryTransaction.objects.filter(school=self.request.user.school)

class IssueStockView(views.APIView):
    """
    Issue inventory items to students or staff members and record transaction.
    """
    permission_classes = [IsApprovedUser]

    def post(self, request):
        item_id = request.data.get('item_id')
        qty = int(request.data.get('quantity', 1))
        recipient = request.data.get('recipient_name', 'Student')
        role = request.data.get('recipient_role', 'Student')
        remarks = request.data.get('remarks', '')
        school = request.user.school

        try:
            item = InventoryItem.objects.get(id=item_id, school=school)
        except InventoryItem.DoesNotExist:
            return Response({'error': 'Inventory item not found.'}, status=status.HTTP_404_NOT_FOUND)

        if item.available_quantity < qty:
            return Response({'error': f'Insufficient stock. Only {item.available_quantity} {item.unit} available.'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            item.allocated_quantity += qty
            item.save()

            txn = InventoryTransaction.objects.create(
                school=school,
                item=item,
                transaction_type='ISSUE',
                quantity=qty,
                recipient_name=recipient,
                recipient_role=role,
                handled_by=request.user,
                remarks=remarks
            )

        return Response({
            'message': f'Issued {qty} {item.unit} of {item.name} to {recipient}',
            'item': InventoryItemSerializer(item).data,
            'transaction': InventoryTransactionSerializer(txn).data
        })

class ReturnStockView(views.APIView):
    """
    Return previously issued items to inventory.
    """
    permission_classes = [IsApprovedUser]

    def post(self, request):
        item_id = request.data.get('item_id')
        qty = int(request.data.get('quantity', 1))
        recipient = request.data.get('recipient_name', '')
        remarks = request.data.get('remarks', '')
        school = request.user.school

        try:
            item = InventoryItem.objects.get(id=item_id, school=school)
        except InventoryItem.DoesNotExist:
            return Response({'error': 'Inventory item not found.'}, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            item.allocated_quantity = max(0, item.allocated_quantity - qty)
            item.save()

            txn = InventoryTransaction.objects.create(
                school=school,
                item=item,
                transaction_type='RETURN',
                quantity=qty,
                recipient_name=recipient,
                handled_by=request.user,
                remarks=remarks
            )

        return Response({
            'message': f'Returned {qty} {item.unit} of {item.name}',
            'item': InventoryItemSerializer(item).data,
            'transaction': InventoryTransactionSerializer(txn).data
        })

class InventorySummaryView(views.APIView):
    """
    Dashboard metrics for Institutional Inventory.
    """
    permission_classes = [IsApprovedUser]

    def get(self, request):
        school = request.user.school
        items = InventoryItem.objects.filter(school=school)
        total_types = items.count()
        low_stock_items = [
            {'id': it.id, 'name': it.name, 'available': it.available_quantity, 'threshold': it.low_stock_threshold, 'unit': it.unit}
            for it in items if it.is_low_stock
        ]

        return Response({
            'total_items_count': total_types,
            'low_stock_alerts_count': len(low_stock_items),
            'low_stock_items': low_stock_items,
        })
