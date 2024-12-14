# apps/userauths/admin.py

from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'phone', 'user_type', 'is_email_verified', 'is_active']
    list_filter = ['user_type', 'is_email_verified', 'is_active']
    search_fields = ['email', 'phone']
    ordering = ['-date_joined']




















# # apps/userauths/admin.py

# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from .models import User, Profile, VendorInvitation, StaffInvitation

# @admin.register(User)
# class CustomUserAdmin(UserAdmin):
#     list_display = ('email', 'username', 'full_name', 'user_type', 'is_active')
#     list_filter = ('user_type', 'is_active', 'is_staff')
#     search_fields = ('email', 'username', 'full_name')
#     ordering = ('-date_joined',)
    
#     def get_fieldsets(self, request, obj=None):
#         # Only show user_type field to superusers
#         fieldsets = super().get_fieldsets(request, obj)
#         if not request.user.is_superuser:
#             fieldsets = [
#                 (section, {'fields': [
#                     f for f in fields if f != 'user_type'
#                 ]}) for section, fields in fieldsets
#             ]
#         return fieldsets

#     def get_readonly_fields(self, request, obj=None):
#         # Make user_type read-only for non-superusers
#         if not request.user.is_superuser:
#             return ['user_type']
#         return []
