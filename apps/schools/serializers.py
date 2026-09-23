from rest_framework import serializers
from .models import School

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = [
            'id', 'school_id', 'name', 'address', 'district',
            'state', 'school_type', 'contact_email', 'contact_phone', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class SchoolPublicCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ['id', 'school_id', 'name', 'district', 'state']
