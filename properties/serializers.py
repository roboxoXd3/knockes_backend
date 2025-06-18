from django.utils import timezone
from django.db.models import Avg, Count
from rest_framework import serializers
from .models import PropertyImage, Property, Amenity, Favorite, PropertyReview
from users.models import OwnerReview


class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ["id", "image", "is_primary"]


class PropertySerializer(serializers.ModelSerializer):
    price_input = serializers.FloatField(write_only=True, required=False)
    images = serializers.SerializerMethodField()
    amenities_display = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    is_boosted = serializers.SerializerMethodField()
    is_featured = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    location_details = serializers.SerializerMethodField()
    price = serializers.FloatField(source="max_price")
    area = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            "id",
            "title",
            "description",
            "price",  # read-only output
            "price_input",  # write-only input
            "address",
            "location",
            "images",
            "bedrooms",
            "bathrooms",
            "area",
            "type",
            "city",
            "state",
            "country",
            "area_sqft",
            "category",
            "furnished",
            "serviced",
            "keyword_tags",
            "created_at",
            "updated_at",
            "amenities",
            "amenities_display",
            "owner",
            "is_boosted",
            "boosted_until",
            "is_featured",
            "featured_until",
            "boost_rank",
            "reviews",
            "location_details",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "owner"]

    def get_images(self, obj):
        return [img.image.url if img.image else "" for img in obj.images.all()]

    def get_amenities_display(self, obj):
        return [a.name for a in obj.amenities.all()]

    def get_owner(self, obj):
        u = obj.owner
        review_stats = OwnerReview.objects.filter(owner=u).aggregate(
            avg_rating=Avg("rating"), total_reviews=Count("id")
        )
        return {
            "id": u.id,
            "name": f"{u.firstname} {u.lastname}",
            "phone": u.telephone,
            "email": u.email,
            "user_type": u.user_type,
            "avatar": (
                u.avatar.url
                if hasattr(u, "avatar") and u.avatar
                else "https://example.com/avatar.jpg"
            ),
            "rating": float(review_stats["avg_rating"] or 0),
            "reviews": review_stats["total_reviews"],
            "whatsapp": getattr(u, "whatsapp", ""),
            "social_links": {
                "linkedin": getattr(u, "linkedin", ""),
                "facebook": getattr(u, "facebook", ""),
                "instagram": getattr(u, "instagram", ""),
                "youtube": getattr(u, "youtube", ""),
                "twitter": getattr(u, "twitter", ""),
            },
        }

    def get_reviews(self, obj):
        reviews = PropertyReview.objects.filter(property=obj).order_by("-created_at")
        return {
            "total_reviews": reviews.count(),
            "average_rating": round(
                reviews.aggregate(avg=Avg("rating"))["avg"] or 0, 1
            ),
            "reviews_list": [
                {
                    "id": i + 1,
                    "user": {
                        "name": f"{r.user.firstname} {r.user.lastname}",
                        "avatar": (
                            r.user.avatar.url
                            if r.user.avatar
                            else "https://example.com/avatar.jpg"
                        ),
                    },
                    "rating": r.rating,
                    "comment": r.comment,
                    "date": r.created_at,
                }
                for i, r in enumerate(reviews)
            ],
        }

    def get_address(self, obj):
        return obj.location

    def get_is_boosted(self, obj):
        return bool(obj.boosted_until and obj.boosted_until > timezone.now())

    def get_is_featured(self, obj):
        return bool(obj.featured_until and obj.featured_until > timezone.now())

    def get_location_details(self, obj):
        return {
            "latitude": getattr(obj, "latitude", None),
            "longitude": getattr(obj, "longitude", None),
        }

    def get_area(self, obj):
        return f"{obj.area_sqft:,} sqft" if obj.area_sqft else None

    def get_price(self, obj):
        return float(obj.max_price or 0)

    def create(self, validated_data):
        amenities_data = validated_data.pop("amenities", [])
        price = validated_data.pop("price_input", None)
        if price is not None:
            validated_data["max_price"] = price

        property_instance = Property.objects.create(**validated_data)
        for name in amenities_data:
            amenity, _ = Amenity.objects.get_or_create(name=name)
            property_instance.amenities.add(amenity)
        return property_instance

    def update(self, instance, validated_data):
        amenities_data = validated_data.pop("amenities", None)
        price = validated_data.pop("price_input", None)
        if price is not None:
            validated_data["max_price"] = price

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if amenities_data is not None:
            instance.amenities.clear()
            for name in amenities_data:
                amenity, _ = Amenity.objects.get_or_create(name=name)
                instance.amenities.add(amenity)

        return instance


class FavoriteSerializer(serializers.ModelSerializer):
    property = PropertySerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ["id", "property", "created_at"]


class PropertyReviewSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = PropertyReview
        fields = ["id", "user", "rating", "comment", "created_at"]
        read_only_fields = ["id", "user", "created_at"]

    def get_user(self, obj):
        return {
            "id": obj.user.id,
            "name": f"{obj.user.firstname} {obj.user.lastname}",
            "avatar": (
                obj.user.avatar.url
                if hasattr(obj.user, "avatar") and obj.user.avatar
                else None
            ),
        }

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user
        property_id = self.context["view"].kwargs.get("property_id")

        # Check for existing review
        existing_review = PropertyReview.objects.filter(
            user=user, property_id=property_id
        ).first()

        if existing_review:
            # Update the existing review
            existing_review.rating = validated_data.get(
                "rating", existing_review.rating
            )
            existing_review.comment = validated_data.get(
                "comment", existing_review.comment
            )
            existing_review.save()
            return existing_review

        # Create new review
        return PropertyReview.objects.create(
            user=user, property_id=property_id, **validated_data
        )
