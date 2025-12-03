from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('mark/', views.mark_attendance, name='mark_attendance'),
    path('bulk-mark/', views.bulk_mark_attendance, name='bulk_mark_attendance'),
    path('list/', views.attendance_list, name='attendance_list'),
    path('reports/', views.reports, name='reports'),
    path('reports/employee-wise/', views.employee_wise_report, name='employee_wise_report'),
    path('reports/export-csv/', views.export_report_csv, name='export_report_csv'),
]
