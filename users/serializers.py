from rest_framework import serializers
from .models import Users


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = [
            "id",
            "firstname",
            "lastname",
            "email",
            "telephone",
            "password",
            "birthdate",
            "gender",
            "is_staff",
            "is_block",
            "created_at",
            "updated_at",
            "user_type",
        ]
        extra_kwargs = {"password": {"write_only": True}}


class UserProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    subscription = serializers.SerializerMethodField()
    profile_completion = serializers.SerializerMethodField()
    verification_status = serializers.SerializerMethodField()

    class Meta:
        model = Users
        fields = [
            "id",
            "email",
            "firstname",
            "lastname",
            "user_type",
            "telephone",
            "avatar",
            "subscription",
            "profile_completion",
            "verification_status",
        ]
        read_only_fields = ["id", "email", "user_type"]

    def get_avatar(self, obj):
        # Replace this logic with actual avatar URL logic
        return (
            obj.avatar.url
            if hasattr(obj, "avatar") and obj.avatar
            else "https://example.com/avatar.jpg"
        )

    def get_subscription(self, obj):
        # Replace with real subscription lookup if available
        return {
            "status": "active",  # "active", "inactive", "expired"
            "plan": "premium",  # "basic", "premium"
            "expires_at": "2024-12-31T23:59:59Z",
            "properties_limit": 50,
            "properties_used": 12,
        }

    def get_profile_completion(self, obj):
        fields = ["firstname", "lastname", "telephone"]
        filled = sum([1 for field in fields if getattr(obj, field)])
        return int((filled / len(fields)) * 100)

    def get_verification_status(self, obj):
        return "verified"
