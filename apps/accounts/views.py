from rest_framework import views, status, permissions, generics
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from .models import User, SchoolJoinRequest
from .serializers import (
    UserSerializer,
    SchoolRegistrationSerializer,
    UserJoinRegistrationSerializer,
    SchoolJoinRequestSerializer
)
from .permissions import IsPrincipal, SameSchoolPermission

class RegisterSchoolView(views.APIView):
    """
    Principal registers a new Ashram School + Principal account.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SchoolRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'School and Principal registered successfully',
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterUserView(views.APIView):
    """
    Teacher, Warden, or Parent registers to join an existing School.
    Creates a pending join request awaiting Principal approval.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserJoinRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': f'Registration submitted successfully! Your account is pending approval by the School Principal of {user.school.name}.',
                'user': UserSerializer(user).data,
                'status': 'PENDING_APPROVAL'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(views.APIView):
    """
    Login endpoint with approval check and school information.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')

        if not username or not password:
            return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if not user:
            return Response({'error': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)

        # Check approval status
        if not user.is_approved:
            return Response({
                'error': 'Account not approved yet.',
                'message': f'Your account registration is currently pending approval by the School Principal of {user.school.name if user.school else "your school"}. Please contact your school administrator.',
                'is_approved': False
            }, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        # Custom claims
        refresh['role'] = user.role
        refresh['school_id'] = user.school.school_id if user.school else None

        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)

class UserProfileView(views.APIView):
    """
    Retrieve authenticated user profile.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

class ListJoinRequestsView(generics.ListAPIView):
    """
    Principal views pending join requests strictly for their own school.
    """
    permission_classes = [IsPrincipal]
    serializer_class = SchoolJoinRequestSerializer

    def get_queryset(self):
        # Strict school isolation
        return SchoolJoinRequest.objects.filter(school=request_user_school(self.request))

def request_user_school(request):
    return request.user.school

class ProcessJoinRequestView(views.APIView):
    """
    Principal approves or rejects a join request.
    """
    permission_classes = [IsPrincipal]

    def post(self, request, pk):
        try:
            join_req = SchoolJoinRequest.objects.get(pk=pk, school=request.user.school)
        except SchoolJoinRequest.DoesNotExist:
            return Response({'error': 'Join request not found in your school.'}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get('action', '').upper()
        if action not in ['APPROVE', 'REJECT']:
            return Response({'error': "Action must be 'APPROVE' or 'REJECT'"}, status=status.HTTP_400_BAD_REQUEST)

        if action == 'APPROVE':
            join_req.status = 'APPROVED'
            join_req.approved_by = request.user
            join_req.approval_date = timezone.now()
            join_req.save()

            # Activate the user
            applicant = join_req.user
            applicant.is_approved = True
            applicant.save()

            return Response({
                'message': f'User {applicant.get_full_name() or applicant.username} approved successfully.',
                'join_request': SchoolJoinRequestSerializer(join_req).data
            })
        else:
            reason = request.data.get('rejection_reason', 'Registration declined by Principal.')
            join_req.status = 'REJECTED'
            join_req.rejection_reason = reason
            join_req.approved_by = request.user
            join_req.approval_date = timezone.now()
            join_req.save()

            applicant = join_req.user
            applicant.is_approved = False
            applicant.save()

            return Response({
                'message': f'User {applicant.get_full_name() or applicant.username} request rejected.',
                'join_request': SchoolJoinRequestSerializer(join_req).data
            })

class StaffListView(generics.ListAPIView):
    """
    Principal lists all approved teachers and wardens belonging to their school.
    """
    permission_classes = [IsPrincipal]
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(
            school=request.user.school if hasattr(self, 'request') else None,
            role__in=['teacher', 'warden'],
            is_approved=True
        )

    def list(self, request, *args, **kwargs):
        queryset = User.objects.filter(
            school=request.user.school,
            role__in=['teacher', 'warden'],
            is_approved=True
        ).order_by('role', 'first_name')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
