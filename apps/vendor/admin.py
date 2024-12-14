# apps/vendors/admin.py
from django.contrib import admin
from .models import VendorProfile, VendorInvitation

@admin.register(VendorProfile)
class VendorProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'business_name', 'is_verified']

@admin.register(VendorInvitation)
class VendorInvitationAdmin(admin.ModelAdmin):
    list_display = ['email', 'business_name', 'is_accepted', 'created_at']