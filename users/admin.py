from django.contrib import admin
from .models import CustomUser, OTPToken


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'email',
        'phone',
        'role',         
        'is_verified',
        'is_active',
        'created_at',
        'last_login'
    ]
    list_filter = [
        'role',          
        'is_verified',
        'is_active',
    ]
    search_fields = ['name', 'email', 'phone']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'last_login']
    fieldsets = [
        ('Personal Information', {
            'fields': ['name', 'email', 'phone']
        }),
        ('Role & Status', {
            'fields': ['role', 'is_verified', 'is_active', 'is_staff', 'is_superuser']
        }),
        ('Important Dates', {
            'fields': ['created_at', 'last_login']
        }),
    ]
    list_per_page = 20

@admin.register(OTPToken)
class OTPTokenAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'otp_code',
        'created_at',
        'expires_at',
        'is_used'
    ]
    list_filter = ['is_used']
    search_fields = ['user__email', 'user__name']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    list_per_page = 20

from .models import SavedProperty

@admin.register(SavedProperty)
class SavedPropertyAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'location', 'price', 'saved_at']
    search_fields = ['user__email', 'title']
    ordering = ['-saved_at']

from .models import UserProperty

@admin.register(UserProperty)
class UserPropertyAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'location', 'price', 'property_type', 'status', 'created_at']
    list_filter = ['status', 'property_type']
    search_fields = ['user__email', 'title', 'location']
    ordering = ['-created_at']