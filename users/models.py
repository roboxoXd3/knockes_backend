from django.db import models

GENDER = [("M", "Male"), ("F", "Female"), ("O", "Other"), ("", "Not selected")]


class Users(models.Model):
    id = models.BigAutoField(primary_key=True)
    firstname = models.CharField(max_length=32)
    lastname = models.CharField(max_length=32)
    email = models.CharField(max_length=96, unique=True)
    telephone = models.CharField(max_length=32)
    password = models.TextField()
    birthdate = models.DateField(null=True, blank=True)
    gender = models.CharField(choices=GENDER, max_length=2, null=True, blank=True)
    is_block = models.BooleanField(default=False)
    user_type = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
