from django.db import models
from django.conf import settings


class Amenity(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "amenities"
        app_label = "properties"


class Property(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    location = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    area_sqft = models.DecimalField(max_digits=10, decimal_places=2)
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    amenities = models.ManyToManyField(Amenity, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "properties"
        app_label = "properties"


class PropertyImage(models.Model):
    property = models.ForeignKey(
        Property, related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="properties/")
    is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = "property_images"
        app_label = "properties"


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorites"
    )
    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name="favorited_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "property")
        db_table = "favorites"
