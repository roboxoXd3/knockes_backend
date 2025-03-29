import jwt
from django.conf import settings
from rest_framework import authentication, exceptions
from users.models import Users
from raininfotech.helper import decodeJwt


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

        try:
            payload = decodeJwt(token)
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Token has expired")
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed("Invalid token")

        try:
            print(payload, "payload>>>>>")
            user = Users.objects.get(id=payload["sub"])
        except Users.DoesNotExist:
            raise exceptions.AuthenticationFailed("User not found")

        return (user, None)
