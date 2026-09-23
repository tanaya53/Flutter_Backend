from rest_framework import serializers
from .models import Announcement, Notification

class AnnouncementSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = Announcement
        fields = [
            'id', 'title', 'message', 'target_role', 'target_class',
            'is_emergency', 'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at']

class NotificationSerializer(serializers.ModelSerializer):
    announcement = AnnouncementSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'announcement', 'is_read', 'read_at']
        read_only_fields = ['id', 'announcement']
