from rest_framework import serializers
from .models import PropertyImage, Property, Amenity, Favorite


class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ["id", "image", "is_primary"]


class PropertySerializer(serializers.ModelSerializer):
    # Output fields
    images = serializers.SerializerMethodField()
    amenities_display = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    is_boosted = serializers.SerializerMethodField()
    boosted_until = serializers.DateTimeField(read_only=True)
    is_featured = serializers.SerializerMethodField()
    featured_until = serializers.DateTimeField(read_only=True)
    boost_rank = serializers.IntegerField(read_only=True)

    # Input-only field
    amenities = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )

    class Meta:
        model = Property
        fields = [
            "id",
            "title",
            "description",
            "location",
            "city",
            "state",
            "country",
            "area_sqft",
            "category",
            "type",
            "bedrooms",
            "bathrooms",
            "mini_price",
            "max_price",
            "furnished",
            "serviced",
            "keyword_tags",
            "created_at",
            "updated_at",
            "images",
            "amenities",
            "amenities_display",
            "owner",
            "is_boosted",
            "boosted_until",
            "is_featured",
            "featured_until",
            "boost_rank",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "owner"]

    def get_images(self, obj):
        return [img.image.url if img.image else "" for img in obj.images.all()]

    def get_amenities_display(self, obj):
        return [a.name for a in obj.amenities.all()]

    def get_owner(self, obj):
        if obj.owner:
            return {
                "id": obj.owner.id,
                "name": f"{obj.owner.firstname} {obj.owner.lastname}",
            }
        return None

    def get_is_boosted(self, obj):
        return bool(obj.boosted_until and obj.boosted_until > timezone.now())

    def get_is_featured(self, obj):
        return bool(obj.featured_until and obj.featured_until > timezone.now())

    def get_boost_rank(self, obj):
        return obj.boost_rank if hasattr(obj, "boost_rank") else 0

    def get_images(self, obj):
        return [img.image.url if img.image else "" for img in obj.images.all()]

    def get_amenities(self, obj):
        return [a.name for a in obj.amenities.all()]

    def get_owner(self, obj):
        u = obj.owner
        return {
            "id": u.id,
            "name": f"{u.firstname} {u.lastname}",
            "phone": u.telephone,
            "email": u.email,
            "user_type": u.user_type,
            "avatar": (
                u.avatar.url if hasattr(u, "avatar") and u.avatar else "avatar.jpg"
            ),
        }

    def get_location_details(self, obj):
        return {
            "address": obj.location,
            "latitude": None,  # Add latitude/longitude in model later if needed
            "longitude": None,
        }

    def get_property_type(self, obj):
        return obj.type

    def get_listing_type(self, obj):
        return obj.category

    def get_price(self, obj):
        return float(obj.max_price or obj.mini_price)

    def get_area(self, obj):
        return f"{obj.area_sqft} sq ft"

    def create(self, validated_data):
        amenities_data = validated_data.pop("amenities", [])
        property_instance = Property.objects.create(**validated_data)
        for name in amenities_data:
            amenity, _ = Amenity.objects.get_or_create(name=name)
            property_instance.amenities.add(amenity)
        return property_instance

    def update(self, instance, validated_data):
        amenities_data = validated_data.pop("amenities", None)
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
