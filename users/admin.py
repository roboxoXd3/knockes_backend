from django.contrib import admin
from .models import Users


class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "firstname",
        "lastname",
        "email",
        "telephone",
        "gender",
        "is_block",
        "user_type",
        "created_at",
    )
    list_filter = ("gender", "is_block", "user_type", "created_at")
    search_fields = ("firstname", "lastname", "email", "telephone")
    ordering = ("-created_at",)


admin.site.register(Users, UserAdmin)
