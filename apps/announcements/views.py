from rest_framework import viewsets, views, status, permissions
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from .models import Announcement, Notification
from .serializers import AnnouncementSerializer, NotificationSerializer
from apps.accounts.permissions import IsApprovedUser, SameSchoolPermission

class AnnouncementViewSet(viewsets.ModelViewSet):
    serializer_class = AnnouncementSerializer
    permission_classes = [IsApprovedUser, SameSchoolPermission]

    def get_queryset(self):
        user = self.request.user
        qs = Announcement.objects.filter(school=user.school)

        # Non-principals only receive announcements meant for ALL or their specific role
        if user.role != 'principal':
            role_mapping = {
                'teacher': 'TEACHERS',
                'warden': 'WARDENS',
                'parent': 'PARENTS',
            }
            target = role_mapping.get(user.role, 'ALL')
            qs = qs.filter(Q(target_role='ALL') | Q(target_role=target))

        is_emergency = self.request.query_params.get('emergency')
        if is_emergency:
            qs = qs.filter(is_emergency=is_emergency.lower() in ('true', '1'))

        return qs

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, created_by=self.request.user)

class MarkNotificationReadView(views.APIView):
    """
    Mark an announcement as read by the user.
    """
    permission_classes = [IsApprovedUser]

    def post(self, request, announcement_id):
        user = request.user
        notification, _ = Notification.objects.get_or_create(
            user=user,
            announcement_id=announcement_id,
            defaults={'is_read': True, 'read_at': timezone.now()}
        )
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        return Response({'message': 'Notification marked as read.'})
