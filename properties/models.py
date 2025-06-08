from django.db import models
from django.conf import settings
from users.models import Users


class Amenity(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "amenities"
        app_label = "properties"


class Property(models.Model):
    CATEGORY_CHOICES = [
        ("sale", "Sale"),
        ("rent", "Rent"),
        ("short_let", "Short Let"),
        ("jv", "Joint Venture"),
        ("rent_to_own", "Rent to Own"),
        ("monthly_rent", "Monthly Rent"),
    ]

    TYPE_CHOICES = [
        ("flat_apartment", "Flat/Apartment"),
        ("terrace", "Terrace"),
        ("detached_house", "Detached House"),
        ("land", "Land"),
        ("joint_venture", "Joint Venture"),
        ("office_space", "Office Space"),
        ("hotel", "Hotel"),
        ("warehouse", "Warehouse"),
        ("shop", "Shop"),
        ("commercial_property", "Commercial Property"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    area_sqft = models.DecimalField(max_digits=10, decimal_places=2)

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='sale')
    type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='flat_apartment')

    bedrooms = models.IntegerField(default=0)
    bathrooms = models.IntegerField(blank=True, null=True, default=0)

    mini_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    max_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    furnished = models.BooleanField(default=False)
    serviced = models.BooleanField(default=False)

    keyword_tags = models.JSONField(default=list, blank=True)

    amenities = models.ManyToManyField(Amenity, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="properties")

    boosted_until = models.DateTimeField(null=True, blank=True)
    featured_until = models.DateTimeField(null=True, blank=True)
    boost_rank = models.IntegerField(default=0)

    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )

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
