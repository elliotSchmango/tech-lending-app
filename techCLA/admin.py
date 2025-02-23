from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User  # Import your User model

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Role", {"fields": ("role",)}),
    )
    list_display = ('username', 'email', 'role', 'is_staff', 'is_superuser')
    list_filter = ('role', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')


admin.site.register(User, CustomUserAdmin)