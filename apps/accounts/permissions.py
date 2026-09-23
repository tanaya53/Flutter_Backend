from rest_framework import permissions

class IsApprovedUser(permissions.BasePermission):
    """
    Allows access only to authenticated users who have been approved by their school principal.
    """
    message = "Your account is currently pending approval by the School Principal."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_approved
        )

class SameSchoolPermission(permissions.BasePermission):
    """
    Strict multi-tenant security rule:
    Ensures that the requested object belongs to the EXACT same school as the authenticated user.
    """
    message = "Access denied: You do not have permission to access resources from another school."

    def has_object_permission(self, request, view, obj):
        if not (request.user and request.user.is_authenticated and request.user.school):
            return False
        
        # Check direct school attribute
        if hasattr(obj, 'school'):
            return obj.school == request.user.school
        # If object is School itself
        if hasattr(obj, 'school_id'):
            return obj == request.user.school
        
        return False

class IsPrincipal(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_approved and
            request.user.role == 'principal'
        )

class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_approved and
            request.user.role == 'teacher'
        )

class IsWarden(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_approved and
            request.user.role == 'warden'
        )

class IsParent(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_approved and
            request.user.role == 'parent'
        )

class IsPrincipalOrTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_approved and
            request.user.role in ['principal', 'teacher']
        )

class IsPrincipalOrWarden(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_approved and
            request.user.role in ['principal', 'warden']
        )
