from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)

GENDER = [("M", "Male"), ("F", "Female"), ("O", "Other"), ("", "Not selected")]


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class Users(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True)
    firstname = models.CharField(max_length=32)
    lastname = models.CharField(max_length=32)
    email = models.EmailField(max_length=96, unique=True)
    telephone = models.CharField(max_length=32, unique=True)
    birthdate = models.DateField(null=True, blank=True)
    gender = models.CharField(choices=GENDER, max_length=2, null=True, blank=True)
    is_block = models.BooleanField(default=False)
    user_type = models.CharField(max_length=255)
    is_staff = models.BooleanField(default=False)  # Required for admin login
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rating = models.FloatField(default=0.0)
    review_count = models.PositiveIntegerField(default=0)

    whatsapp = models.CharField(max_length=32, null=True, blank=True)

    linkedin = models.URLField(null=True, blank=True)
    facebook = models.URLField(null=True, blank=True)
    instagram = models.URLField(null=True, blank=True)
    youtube = models.URLField(null=True, blank=True)
    twitter = models.URLField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["firstname", "lastname", "telephone"]

    objects = UserManager()

    class Meta:
        db_table = "users"
        app_label = "users"

    def __str__(self):
        return self.firstname + " " + self.lastname


class UserTokenLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.BigIntegerField()
    user_token = models.CharField(max_length=255)
    is_block = models.IntegerField(default=0)
    created_at = models.DateTimeField(
        auto_now_add=True
    )  # Automatically set on creation
    updated_at = models.DateTimeField(
        auto_now=True
    )  # Automatically update on modification

    class Meta:
        db_table = "user_token_logs"  # Explicitly specifying table name
        verbose_name = "User Token Log"
        verbose_name_plural = "User Token Logs"

    def __str__(self):
        return f"Token Log for User {self.user_id}"


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class OwnerReview(models.Model):
    id = models.BigAutoField(primary_key=True)  # ✅ Add this line
    owner = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name="owner_reviews"
    )
    reviewer = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name="given_owner_reviews"
    )
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("owner", "reviewer")
        ordering = ["-created_at"]
