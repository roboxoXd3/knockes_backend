from rest_framework import authentication, exceptions
from users.models import Users
from raininfotech.helper import decodeJwt
from users.utils import is_token_blacklisted


class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return None

        try:
            prefix, token = auth_header.split(" ")
            if prefix.lower() != "bearer":
                raise exceptions.AuthenticationFailed("Invalid token prefix")
        except ValueError:
            raise exceptions.AuthenticationFailed("Invalid Authorization header format")

        # ✅ Check blacklist
        if is_token_blacklisted(token):
            raise exceptions.AuthenticationFailed("Token has been blacklisted")

        # ✅ Decode JWT with proper fallback
        payload = None
        try:
            payload = decodeJwt(token)
        except Exception:
            raise exceptions.AuthenticationFailed("Invalid or expired token")

        if not payload or not payload.get("sub"):
            raise exceptions.AuthenticationFailed("Invalid or expired token")

        # ✅ Get user
        try:
            user = Users.objects.get(id=payload["sub"])
        except Users.DoesNotExist:
            raise exceptions.AuthenticationFailed("User not found")

        return (user, None)
