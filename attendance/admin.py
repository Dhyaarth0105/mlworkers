from django.contrib import admin
from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'status', 'ot_hours', 'marked_by', 'marked_at']
    list_filter = ['status', 'date', 'marked_by']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_code']
    readonly_fields = ['marked_at', 'marked_by']
    date_hierarchy = 'date'
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.marked_by = request.user
        super().save_model(request, obj, form, change)
