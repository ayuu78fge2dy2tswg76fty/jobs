from django.contrib import admin
from .models import PasswordResetOTP

# Register your models here.
@admin.register(PasswordResetOTP)
class PasswordResetOTPAdmin(admin.ModelAdmin):
    list_display = ('email', 'user_type', 'otp', 'is_used', 'created_at')
    list_filter = ('user_type', 'is_used', 'created_at')
    search_fields = ('email', 'otp')
