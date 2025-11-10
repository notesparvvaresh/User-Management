from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("id", "phone_number", "username", "is_staff", "is_active")
    ordering = ("phone_number",)

    fieldsets = (
        (None, {"fields": ("phone_number", "username", "password")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login",)}),
    )
    add_fieldsets = ((None, {"fields": ("phone_number", "password1", "password2")}),)
    search_fields = ("phone_number", "username")
    readonly_fields = ("last_login",)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "full_name")
    search_fields = ("user__phone_number", "full_name")
