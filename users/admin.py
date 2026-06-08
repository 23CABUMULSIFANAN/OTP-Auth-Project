from django.contrib import admin
from .models import CustomUser, OTPToken


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'email',
        'phone',
        'role',          # ← add this
        'is_verified',
        'is_active',
        'created_at',
        'last_login'
    ]
    list_filter = [
        'role',          # ← add this
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