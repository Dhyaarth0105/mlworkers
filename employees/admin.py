from django.contrib import admin
from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_code', 'get_full_name', 'company', 'designation', 'is_active', 'date_of_joining']
    list_filter = ['company', 'is_active', 'date_of_joining']
    search_fields = ['employee_code', 'first_name', 'last_name', 'designation']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'
