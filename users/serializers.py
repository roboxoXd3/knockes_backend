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
            "is_block",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {"password": {"write_only": True}}
