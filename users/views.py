import bcrypt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from raininfotech.helper import create_token512
from .serializers import UserSerializer
import traceback
from django.db import transaction
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


@api_view(["POST"])
@transaction.atomic
def register_user(request):
    reqData = request.data

    # Validate required fields
    if not reqData.get("email") or not reqData.get("telephone"):
        return Response(
            {"error": "Please enter all the required details (email and telephone)."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        print("Starting registration process...")

        hashed_password = bcrypt.hashpw(
            reqData["password"].encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        reqData["password"] = (
            hashed_password  # Replace plain text password with hashed one
        )

        serializer = UserSerializer(data=request.data)
        print("Serializer initialized...")

        # Check if data is valid
        if serializer.is_valid():
            # Start atomic transaction
            with transaction.atomic():
                user = serializer.save()
                print("User saved successfully...")

                # Token generation
                create_token512(user)
                print("Token generated...")

                # Successful response
                return Response(
                    {
                        "message": "User registered successfully",
                        "username": f"{user.firstname} {user.lastname}",
                        "user_id": user.id
                    },
                    status=status.HTTP_201_CREATED,
                )

        # If validation fails
        print("Validation failed, rolling back transaction.")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Handle unexpected exceptions
    except Exception as e:
        print("Exception occurred:", e)
        print(traceback.format_exc())  # Print full traceback
        transaction.set_rollback(True)  # Rollback the transaction
        return Response(
            {
                "error": "Something went wrong during user registration.",
                "details": str(e),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def redis_set(key, value, expiry):
    cache.set(key, value, timeout=expiry)


@api_view(["POST"])
def mobile_login(request):
    req_data = request.data
    print("REQ DATA >>>", req_data)

    which_login = req_data.get("is_shopper_login", False)
    data = {}

    if not req_data.get("telephone"):
        return Response(
            {"error": "Telephone is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    telephone = data_sanitization(req_data["telephone"])
    print(f"Sanitized Telephone: {telephone}")

    if not phone_no_validation(telephone):
        return Response(
            {"error": "Enter a valid mobile number"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # ORM Query
        user = Users.objects.filter(telephone=telephone).first()
        print(f"User fetched from DB: {user}")

        if not user:
            return Response(
                {"error": "Phone number doesn't exist"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not user and not which_login:
            return Response(
                {"error": "Invalid Credentials"}, status=status.HTTP_400_BAD_REQUEST
            )

        if user.is_block:
            return Response(
                {"error": "Your account has been blocked, please contact support"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        msg = "log in"
        platform = request.data.get("platform", "web")  # Changed to data
        otp = send_otp_for_two_fa_verification(telephone, msg, platform)

        if not otp:
            return Response(
                {"error": "Something went wrong, please try again."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Update data in cache (Redis)
        data = {
            "otp": otp,
            "id": user.id if user else "",
            "is_new_user": 0 if user and user.email else 1,
        }
        print("Data to be set in Redis:", data)

        redis_set(telephone, data, expiry=300)  # 5 minutes expiry

        response = {
            "otp": otp,
            "msg": "OTP sent successfully",
            "is_otp_sent": True,
            "isRegistered": True,
        }
        return Response(response, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"Exception: {e}")
        return Response(
            {"error": "An error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
