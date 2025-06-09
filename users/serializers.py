from rest_framework import serializers
from .models import Users, OwnerReview


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
    social_links = serializers.SerializerMethodField()

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
            "rating",
            "reviews",
            "whatsapp",
            "linkedin",
            "facebook",
            "instagram",
            "youtube",
            "twitter",
            "social_links",
            "subscription",
            "profile_completion",
            "verification_status",
        ]
        read_only_fields = [
            "id",
            "email",
            "user_type",
            "avatar",
            "social_links",
            "subscription",
            "profile_completion",
            "verification_status",
        ]

    def get_avatar(self, obj):
        return (
            obj.avatar.url
            if hasattr(obj, "avatar") and obj.avatar
            else "https://example.com/avatar.jpg"
        )

    def get_subscription(self, obj):
        return {
            "status": "active",  # Replace with dynamic logic if needed
            "plan": "premium",
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

    def get_social_links(self, obj):
        return {
            "linkedin": obj.linkedin,
            "facebook": obj.facebook,
            "instagram": obj.instagram,
            "youtube": obj.youtube,
            "twitter": obj.twitter,
        }


class OwnerReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.SerializerMethodField()

    class Meta:
        model = OwnerReview
        fields = ["id", "reviewer", "rating", "comment", "created_at"]

    def get_reviewer(self, obj):
        return {
            "name": f"{obj.reviewer.firstname} {obj.reviewer.lastname}",
            "avatar": (
                obj.reviewer.avatar.url
                if hasattr(obj.reviewer, "avatar") and obj.reviewer.avatar
                else None
            ),
        }

    def create(self, validated_data):
        request = self.context["request"]
        reviewer = request.user
        owner_id = self.context["view"].kwargs.get("owner_id")

        existing = OwnerReview.objects.filter(
            owner_id=owner_id, reviewer=reviewer
        ).first()

        if existing:
            existing.rating = validated_data.get("rating", existing.rating)
            existing.comment = validated_data.get("comment", existing.comment)
            existing.save()
            self.update_owner_stats(owner_id)
            return existing

        review = OwnerReview.objects.create(
            owner_id=owner_id, reviewer=reviewer, **validated_data
        )
        self.update_owner_stats(owner_id)
        return review

    def update_owner_stats(self, owner_id):
        from django.db.models import Avg, Count

        owner = Users.objects.get(id=owner_id)
        stats = OwnerReview.objects.filter(owner=owner).aggregate(
            avg=Avg("rating"), count=Count("id")
        )
        owner.rating = stats["avg"] or 0
        owner.review_count = stats["count"]
        owner.save()
