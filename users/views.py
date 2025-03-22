import bcrypt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from raininfotech.helper import create_token512
from .serializers import UserSerializer
import traceback
from django.db import transaction


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
