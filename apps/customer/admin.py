# apps/customers/admin.py
from django.contrib import admin
from .models import CustomerProfile

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'gender']
    search_fields = ['user__email', 'first_name', 'last_name']