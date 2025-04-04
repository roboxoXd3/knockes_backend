from rest_framework import serializers
from .models import PropertyImage, Property, Amenity


class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ["id", "image", "is_primary"]


class PropertySerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)

    # ✅ For input only (POST/PUT)
    amenities = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )

    # ✅ For output only (GET)
    amenities_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Property
        fields = "__all__"

    def get_amenities_display(self, obj):
        return [amenity.name for amenity in obj.amenities.all()]

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
