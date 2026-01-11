from rest_framework import permissions

class IsCoordinatorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow event coordinators to edit their own events.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the coordinator or superuser
        return obj.coordinator == request.user or request.user.is_superuser