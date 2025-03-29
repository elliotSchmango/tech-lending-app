from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Item, Collection

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets

    list_display = ('username', 'email', 'get_groups', 'is_staff', 'is_superuser')
    list_filter = ('groups', 'is_staff', 'is_superuser') 
    search_fields = ('username', 'email')

    def get_groups(self, obj):
        """Display the user's groups in the admin panel."""
        return ", ".join(group.name for group in obj.groups.all()) if obj.groups.exists() else "No Group"
    
    get_groups.short_description = "Groups"  # Set column title in the admin panel

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'visibility', 'creator') 
    search_fields = ('name', 'description') 
    list_filter = ('visibility',) 
    ordering = ('name',)

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'identifier', 'status', 'rating') 
    search_fields = ('title',) 
    list_filter = ('status',)  
    ordering = ('title',)

