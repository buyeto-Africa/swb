from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .models import User, UserInvitation


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'user_type', 'company_name', 
                   'is_approved', 'is_staff')
    list_filter = ('user_type', 'is_approved', 'is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name', 'company_name')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone_number', 'company_name')}),
        (_('Type and Status'), {
            'fields': ('user_type', 'is_approved', 'is_active'),
            'classes': ('wide',)
        }),
        (_('Permissions'), {
            'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    
    actions = ['approve_users', 'unapprove_users']
    
    def approve_users(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, _(
            '%(count)d user(s) were successfully approved.'
        ) % {'count': updated})
    approve_users.short_description = _("Approve selected users")
    
    def unapprove_users(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, _(
            '%(count)d user(s) were successfully unapproved.'
        ) % {'count': updated})
    unapprove_users.short_description = _("Unapprove selected users")


@admin.register(UserInvitation)
class UserInvitationAdmin(admin.ModelAdmin):
    list_display = ('email', 'user_type', 'invited_by', 'created_at', 'expires_at',
                   'is_used', 'email_sent', 'is_expired')
    list_filter = ('user_type', 'is_used', 'email_sent')
    search_fields = ('email', 'invited_by__email')
    readonly_fields = ('token', 'created_at', 'expires_at', 'email_sent', 'email_sent_at')
    
    fieldsets = (
        (None, {
            'fields': ('email', 'user_type')
        }),
        (_('Invitation Details'), {
            'fields': ('token', 'invited_by', 'expires_at')
        }),
        (_('Status'), {
            'fields': ('is_used', 'email_sent', 'email_sent_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set invited_by on creation
            obj.invited_by = request.user
        super().save_model(request, obj, form, change)
    
    def is_expired(self, obj):
        return obj.is_expired
    is_expired.boolean = True
    is_expired.short_description = _('Expired')
