from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Item, Collection

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets

    list_display = ('username', 'email', 'get_groups', 'is_staff', 'is_superuser')
    list_filter = ('groups', 'is_staff', 'is_superuser') 
    search_fields = ('username', 'email')

    def get_groups(self, obj):
        """Display the user's groups in the admin panel."""
        return ", ".join(group.name for group in obj.groups.all()) if obj.groups.exists() else "No Group"
    
    get_groups.short_description = "Groups"  # Set column title in the admin panel

class ItemInline(admin.TabularInline):
    model = Collection.items.through 
    extra = 1

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'visibility')
        }),
        ('Permissions', {
            'fields': ('creator', 'allowed_users'),
            'description': "Control who can access this collection"
        }),
    )
    
    inlines = [ItemInline]
    readonly_fields = ['creator']
    # List configuration
    list_display = ('name', 'visibility', 'creator')
    search_fields = ('name', 'description')
    list_filter = ('visibility',)

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'identifier', 'status', 'rating') 
    search_fields = ('title',) 
    list_filter = ('status',)  
    ordering = ('title',)

