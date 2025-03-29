from django.db import transaction, IntegrityError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from raininfotech.helper import create_token
from .serializers import UserSerializer
import traceback
from django.core.cache import cache
from users.models import Users
from users.utils import (
    data_sanitization,
    phone_no_validation,
    send_otp_for_two_fa_verification,
)


@api_view(["GET"])
def health_check(request):
    return Response(
        {"status": "OK", "message": "Health check passed."}, status=status.HTTP_200_OK
    )


def cache_set(key, value, expiry=300):
    cache.set(key, value, timeout=expiry)


@api_view(["POST"])
@permission_classes([AllowAny])
def register_user(request):
    req_data = request.data

    if (
        not req_data.get("email")
        or not req_data.get("telephone")
        or not req_data.get("password")
    ):
        return Response(
            {"error": "Email, telephone, and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        # Check for duplicates manually (optional, improves UX)
        if Users.objects.filter(email=req_data["email"]).exists():
            return Response(
                {"error": "Email already exists."}, status=status.HTTP_409_CONFLICT
            )

        if Users.objects.filter(telephone=req_data["telephone"]).exists():
            return Response(
                {"error": "Phone number already exists."},
                status=status.HTTP_409_CONFLICT,
            )

        req_data["password"] = make_password(req_data["password"])
        serializer = UserSerializer(data=req_data)

        if serializer.is_valid():
            with transaction.atomic():
                user = serializer.save()
                token = create_token(user)
                return Response(
                    {
                        "message": "User registered successfully",
                        "username": f"{user.firstname} {user.lastname}",
                        "user_id": user.id,
                        "token": token,
                    },
                    status=status.HTTP_201_CREATED,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except IntegrityError as e:
        return Response(
            {"error": "User with this email or phone already exists."},
            status=status.HTTP_409_CONFLICT,
        )

    except Exception as e:
        print(traceback.format_exc())
        return Response(
            {"error": "Registration failed", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
def user_login(request):
    req_data = request.data

    # Login via telephone (OTP)
    if req_data.get("telephone"):
        telephone = data_sanitization(req_data.get("telephone"))
        if not phone_no_validation(telephone):
            return Response(
                {"error": "Enter a valid mobile number"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = Users.objects.filter(telephone=telephone).first()
        if not user:
            return Response(
                {"error": "Phone number doesn't exist"},
                status=status.HTTP_403_FORBIDDEN,
            )
        if user.is_block:
            return Response(
                {"error": "Account blocked"}, status=status.HTTP_401_UNAUTHORIZED
            )

        otp = send_otp_for_two_fa_verification(
            telephone, "log in", request.data.get("platform", "web")
        )
        if not otp:
            return Response(
                {"error": "OTP failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        cache_data = {
            "otp": otp,
            "id": user.id,
            "is_new_user": 0 if user.email else 1,
        }
        cache_set(telephone, cache_data)
        return Response(
            {
                "otp": otp,
                "msg": "OTP sent successfully",
                "is_otp_sent": True,
                "isRegistered": True,
            },
            status=status.HTTP_200_OK,
        )

    # Login via email + password
    elif req_data.get("email") and req_data.get("password"):
        email = req_data.get("email")
        password = req_data.get("password")

        if not email_validation(email):
            return Response(
                {"error": "Invalid email"}, status=status.HTTP_400_BAD_REQUEST
            )

        user = Users.objects.filter(email=email).first()
        if not user:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
        if user.is_block:
            return Response(
                {"error": "Account blocked"}, status=status.HTTP_401_UNAUTHORIZED
            )

        if not check_password(password, user.password):
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

        token = create_token(user)
        return Response(
            {
                "token": token,
                "user_id": user.id,
                "email": user.email,
                "msg": "Login successful",
            },
            status=status.HTTP_200_OK,
        )

    return Response(
        {"error": "Invalid login request"}, status=status.HTTP_400_BAD_REQUEST
    )


@api_view(["POST"])
def verify_otp_login(request):
    req_data = request.data
    telephone = req_data.get("telephone")
    otp = str(req_data.get("otp"))

    if not telephone or not otp:
        return Response(
            {"error": "Telephone and OTP are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    cached_data = cache.get(telephone)
    print("Cached Data:", cached_data)

    if not cached_data:
        return Response(
            {"error": "OTP expired or invalid. Please request a new one."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    stored_otp = str(cached_data.get("otp"))
    user_id = cached_data.get("id")

    if otp != stored_otp:
        return Response({"error": "Invalid OTP"}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        user = Users.objects.get(id=user_id)
    except Users.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    if not verify_user_status(user):
        return Response(
            {"error": "Your account is blocked. Please contact support."},
            status=status.HTTP_403_FORBIDDEN,
        )

    token = create_token(user)

    # You can optionally delete OTP from cache after successful use
    cache.delete(telephone)

    return Response(
        {
            "message": "Login successful",
            "token": token,
            "user_id": user.id,
            "is_new_user": cached_data.get("is_new_user", 0),
        },
        status=status.HTTP_200_OK,
    )


def verify_user_status(user):
    if user.is_block:
        return False
    return True

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard(request):
    return Response({"message": f"Welcome {request.user.firstname}!"})
