from rest_framework.permissions import BasePermission, SAFE_METHODS


class ReadOnlyOrAuthenticated(BasePermission):
    """
    Allows unrestricted access to safe (read-only) methods,
    but requires authentication for unsafe (write) methods.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:  # GET, HEAD, OPTIONS
            return True
        return request.user and request.user.is_authenticated
