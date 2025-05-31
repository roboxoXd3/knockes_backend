import random
from rest_framework.views import APIView
from django.db import transaction, IntegrityError
from django.core.cache import cache
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password, check_password
from rest_framework import status, generics, permissions
from raininfotech.helper import create_token, email_validation, cache_set
from .serializers import UserSerializer, UserProfileSerializer
import traceback
from users.models import Users, UserTokenLog
from users.utils import (
    data_sanitization,
    phone_no_validation,
    send_otp_for_two_fa_verification,
    blacklist_token,
)


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            {"status": "OK", "message": "Health check passed and working welll", "version": "v1.1", "deployment": "CI/CD Test"},
            status=status.HTTP_200_OK,
        )


class RegisterUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
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

        except IntegrityError:
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


class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        req_data = request.data

        # ✅ Login via telephone (OTP-based)
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
                    {"error": "Account blocked"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            otp = send_otp_for_two_fa_verification(
                telephone, "log in", req_data.get("platform", "web")
            )
            if not otp:
                return Response(
                    {"error": "OTP failed"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
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

        # ✅ Login via email + password
        elif req_data.get("email") and req_data.get("password"):
            email = req_data.get("email")
            password = req_data.get("password")

            if not email_validation(email):
                return Response(
                    {"error": "Invalid email"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = Users.objects.filter(email=email).first()
            if not user:
                return Response(
                    {"error": "User not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if user.is_block:
                return Response(
                    {"error": "Account blocked"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            if not check_password(password, user.password):
                return Response(
                    {"error": "Invalid credentials"},
                    status=status.HTTP_401_UNAUTHORIZED,
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

        # ❌ Invalid input
        return Response(
            {"error": "Invalid login request"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class VerifyOtpLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
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
            return Response(
                {"error": "Invalid OTP"}, status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if not verify_user_status(user):
            return Response(
                {"error": "Your account is blocked. Please contact support."},
                status=status.HTTP_403_FORBIDDEN,
            )

        token = create_token(user)

        # Optional: Delete OTP from cache after successful login
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


class LogoutUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return Response(
                {"error": "Authorization token missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            prefix, token = auth_header.split(" ")
            if prefix.lower() != "bearer":
                return Response(
                    {"error": "Invalid token prefix"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except ValueError:
            return Response(
                {"error": "Invalid Authorization header format"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Block token in DB
        token_log = UserTokenLog.objects.filter(
            user_id=user.id, user_token=token
        ).first()

        if token_log:
            token_log.is_block = True
            token_log.save()
        else:
            UserTokenLog.objects.create(
                user_id=user.id, user_token=token, is_block=True
            )

        # Blacklist in Redis
        blacklist_token(token)

        return Response(
            {"message": "Successfully logged out."}, status=status.HTTP_200_OK
        )


class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        identifier = request.data.get("email") or request.data.get("telephone")
        otp = request.data.get("otp")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        if not identifier:
            return Response(
                {"error": "Email or telephone is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 🔹 CASE 1: Send OTP
        if not otp and not new_password:
            user = self._get_user(identifier)
            if not user:
                return Response(
                    {"error": "No user found."}, status=status.HTTP_404_NOT_FOUND
                )
            if user.is_block:
                return Response(
                    {"error": "User account is blocked."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            otp = random.randint(100000, 999999)
            cache.set(
                f"password_reset:{identifier}",
                {
                    "otp": str(otp),
                    "user_id": user.id,
                },
                timeout=300,
            )  # 5 minutes

            send_otp_for_two_fa_verification(
                identifier, msg="reset password", platform="web"
            )

            return Response(
                {
                    "message": "OTP sent successfully for password reset",
                    "otp": otp,  # 🚨 Dev only — remove in production!
                },
                status=status.HTTP_200_OK,
            )

        # 🔹 CASE 2: Verify OTP + Reset Password
        if otp and new_password and confirm_password:
            data = cache.get(f"password_reset:{identifier}")
            if not data:
                return Response(
                    {"error": "OTP expired or invalid."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if str(data.get("otp")) != str(otp):
                return Response(
                    {"error": "Invalid OTP."}, status=status.HTTP_401_UNAUTHORIZED
                )

            if new_password != confirm_password:
                return Response(
                    {"error": "Passwords do not match."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                user = Users.objects.get(id=data.get("user_id"))
            except Users.DoesNotExist:
                return Response(
                    {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
                )

            if check_password(new_password, user.password):
                return Response(
                    {"error": "New password cannot be the same as the old password."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.password = make_password(new_password)
            user.save()
            cache.delete(f"password_reset:{identifier}")

            return Response(
                {"message": "Password reset successful."}, status=status.HTTP_200_OK
            )

        # 🔹 CASE 3: Incomplete Data
        return Response(
            {
                "error": "Incomplete data. Provide either just identifier or full reset info (otp, new_password, confirm_password)."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def _get_user(self, identifier):
        try:
            if "@" in identifier:
                return Users.objects.filter(email=identifier).first()
            return Users.objects.filter(telephone=identifier).first()
        except Exception:
            return None


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
