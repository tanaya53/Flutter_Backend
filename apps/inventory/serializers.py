from rest_framework import serializers
from .models import InventoryItem, InventoryTransaction

class InventoryItemSerializer(serializers.ModelSerializer):
    available_quantity = serializers.IntegerField(read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = InventoryItem
        fields = [
            'id', 'name', 'category', 'total_quantity', 'allocated_quantity',
            'available_quantity', 'unit', 'low_stock_threshold', 'is_low_stock',
            'storage_location', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class InventoryTransactionSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    handled_by_name = serializers.CharField(source='handled_by.get_full_name', read_only=True)

    class Meta:
        model = InventoryTransaction
        fields = [
            'id', 'item', 'item_name', 'transaction_type', 'quantity',
            'recipient_name', 'recipient_role', 'handled_by', 'handled_by_name',
            'remarks', 'date'
        ]
        read_only_fields = ['id', 'handled_by', 'date']
