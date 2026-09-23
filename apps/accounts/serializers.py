from rest_framework import serializers
from django.db import transaction
from django.contrib.auth import get_user_model
from apps.schools.models import School
from apps.schools.serializers import SchoolSerializer
from .models import SchoolJoinRequest, TeacherProfile, WardenProfile

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    school_details = SchoolSerializer(source='school', read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'full_name',
            'email', 'role', 'phone_number', 'is_approved', 'school',
            'school_details', 'date_joined'
        ]
        read_only_fields = ['id', 'is_approved', 'date_joined']

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username

class SchoolRegistrationSerializer(serializers.Serializer):
    school_name = serializers.CharField(max_length=255)
    school_id = serializers.CharField(max_length=50)
    address = serializers.CharField(required=False, allow_blank=True)
    district = serializers.CharField(max_length=100)
    state = serializers.CharField(max_length=100, default='Maharashtra')
    school_type = serializers.CharField(max_length=50, default='GOVT_ASHRAM')
    
    principal_name = serializers.CharField(max_length=150)
    principal_email = serializers.EmailField()
    principal_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=6)

    def validate_school_id(self, value):
        val = value.strip().upper()
        if School.objects.filter(school_id__iexact=val).exists():
            raise serializers.ValidationError(f"School ID '{val}' is already registered. Each school must have a unique ID.")
        return val

    def validate_username(self, value):
        val = value.strip()
        if User.objects.filter(username__iexact=val).exists():
            raise serializers.ValidationError(f"Username '{val}' is already taken.")
        return val

    def create(self, validated_data):
        with transaction.atomic():
            school = School.objects.create(
                school_id=validated_data['school_id'],
                name=validated_data['school_name'],
                address=validated_data.get('address', ''),
                district=validated_data['district'],
                state=validated_data.get('state', 'Maharashtra'),
                school_type=validated_data.get('school_type', 'GOVT_ASHRAM'),
                contact_email=validated_data['principal_email'],
                contact_phone=validated_data.get('principal_phone', ''),
            )

            name_parts = validated_data['principal_name'].strip().split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''

            user = User.objects.create_user(
                username=validated_data['username'],
                email=validated_data['principal_email'],
                password=validated_data['password'],
                first_name=first_name,
                last_name=last_name,
                phone_number=validated_data.get('principal_phone', ''),
                role='principal',
                school=school,
                is_approved=True  # Principal who registered the school is automatically approved
            )

            return user

class UserJoinRegistrationSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=150)
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone_number = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True, min_length=6)
    role = serializers.ChoiceField(choices=[('teacher', 'Teacher'), ('warden', 'Warden'), ('parent', 'Parent')])
    school_id = serializers.CharField(max_length=50)

    def validate_school_id(self, value):
        val = value.strip().upper()
        try:
            school = School.objects.get(school_id__iexact=val)
            self.context['school'] = school
            return val
        except School.DoesNotExist:
            raise serializers.ValidationError(f"School ID '{val}' does not exist.")

    def validate_username(self, value):
        val = value.strip()
        if User.objects.filter(username__iexact=val).exists():
            raise serializers.ValidationError(f"Username '{val}' is already taken.")
        return val

    def create(self, validated_data):
        school = self.context['school']
        name_parts = validated_data['full_name'].strip().split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        with transaction.atomic():
            user = User.objects.create_user(
                username=validated_data['username'],
                email=validated_data.get('email', ''),
                password=validated_data['password'],
                first_name=first_name,
                last_name=last_name,
                phone_number=validated_data['phone_number'],
                role=validated_data['role'],
                school=school,
                is_approved=False  # Requires Principal approval
            )

            if user.role == 'teacher':
                TeacherProfile.objects.create(user=user, school=school)
            elif user.role == 'warden':
                WardenProfile.objects.create(user=user, school=school)

            SchoolJoinRequest.objects.create(
                user=user,
                school=school,
                requested_role=user.role,
                status='PENDING'
            )

            return user

class SchoolJoinRequestSerializer(serializers.ModelSerializer):
    applicant_name = serializers.CharField(source='user.get_full_name', read_only=True)
    applicant_username = serializers.CharField(source='user.username', read_only=True)
    applicant_email = serializers.CharField(source='user.email', read_only=True)
    applicant_phone = serializers.CharField(source='user.phone_number', read_only=True)
    school_name = serializers.CharField(source='school.name', read_only=True)
    school_code = serializers.CharField(source='school.school_id', read_only=True)

    class Meta:
        model = SchoolJoinRequest
        fields = [
            'id', 'user', 'applicant_name', 'applicant_username',
            'applicant_email', 'applicant_phone', 'school',
            'school_name', 'school_code', 'requested_role',
            'status', 'request_date', 'approved_by', 'approval_date',
            'rejection_reason'
        ]
        read_only_fields = ['id', 'user', 'school', 'request_date', 'approved_by', 'approval_date']
