# apps/staff/admin.py
from django.contrib import admin
from .models import StaffProfile, StaffRole, StaffInvitation

@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'is_active']

@admin.register(StaffRole)
class StaffRoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'staff_count']

@admin.register(StaffInvitation)
class StaffInvitationAdmin(admin.ModelAdmin):
    list_display = ['email', 'role', 'is_accepted', 'created_at']