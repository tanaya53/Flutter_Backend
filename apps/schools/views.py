from rest_framework import views, status, permissions
from rest_framework.response import Response
from .models import School
from .serializers import SchoolSerializer, SchoolPublicCheckSerializer

class VerifySchoolIdView(views.APIView):
    """
    Public endpoint to check if a School ID exists when a user enters it to join a school.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        school_id = request.query_params.get('school_id', '').strip()
        if not school_id:
            return Response({'error': 'School ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            school = School.objects.get(school_id__iexact=school_id)
            return Response({
                'found': True,
                'school': SchoolPublicCheckSerializer(school).data
            }, status=status.HTTP_200_OK)
        except School.DoesNotExist:
            return Response({
                'found': False,
                'error': f'School ID {school_id} not found.'
            }, status=status.HTTP_404_NOT_FOUND)

class CurrentSchoolView(views.APIView):
    """
    Returns the authenticated user's school profile.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not request.user.school:
            return Response({'error': 'No school associated with this user.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = SchoolSerializer(request.user.school)
        return Response(serializer.data)
