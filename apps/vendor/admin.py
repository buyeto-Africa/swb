# apps/vendors/admin.py

from django.contrib import admin
from .models import VendorInvitation

@admin.register(VendorInvitation)
class VendorInvitationAdmin(admin.ModelAdmin):
    list_display = ['email', 'business_name', 'is_accepted', 'created_at', 'expires_at']
    list_filter = ['is_accepted']
    search_fields = ['email', 'business_name']
    readonly_fields = ['token']
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('email', 'business_name')
        return self.readonly_fields