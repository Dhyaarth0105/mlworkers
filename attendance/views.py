from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Sum, F, DecimalField
from django.db.models.functions import Coalesce
from django.http import JsonResponse, HttpResponse
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from accounts.decorators import admin_required
from .models import Attendance
from .forms import AttendanceForm, BulkAttendanceForm, AttendanceReportFilterForm
from employees.models import Employee
from companies.models import Company
import csv


def get_min_allowed_date():
    """Get minimum allowed date (3 months ago from today)"""
    return date.today() - relativedelta(months=3)


def validate_date_range(from_date_str, to_date_str):
    """Validate and enforce 3-month date restriction"""
    min_date = get_min_allowed_date()
    today = date.today()
    
    # Parse and validate from_date
    if from_date_str:
        try:
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
            if from_date < min_date:
                from_date = min_date
        except:
            from_date = min_date
    else:
        from_date = today.replace(day=1)
    
    # Parse and validate to_date
    if to_date_str:
        try:
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
            if to_date > today:
                to_date = today
        except:
            to_date = today
    else:
        to_date = today
    
    return from_date.strftime('%Y-%m-%d'), to_date.strftime('%Y-%m-%d')


@login_required
def mark_attendance(request):
    """Mark attendance for employees (Supervisor view)"""
    if request.method == 'POST':
        form = AttendanceForm(request.POST, user=request.user)
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.marked_by = request.user
            try:
                attendance.save()
                messages.success(request, f'Attendance marked for {attendance.employee.get_full_name()}')
                return redirect('attendance:mark_attendance')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
    else:
        form = AttendanceForm(initial={'date': date.today()}, user=request.user)
    
    # Get today's attendance for assigned employees
    if request.user.is_supervisor():
        assigned_employees = request.user.get_assigned_employees()
        today_attendance = Attendance.objects.filter(
            date=date.today(),
            employee__in=assigned_employees
        ).select_related('employee', 'employee__company')
    else:
        today_attendance = Attendance.objects.filter(
            date=date.today()
        ).select_related('employee', 'employee__company')
    
    context = {
        'form': form,
        'today_attendance': today_attendance,
    }
    return render(request, 'attendance/mark_attendance.html', context)


@login_required
def bulk_mark_attendance(request):
    """Bulk attendance marking interface - Main supervisor screen"""
    today = date.today()
    
    # For supervisors, default to today and validate date
    if request.user.is_supervisor():
        selected_date = request.GET.get('date', str(today))
        try:
            selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
            # Only allow today or admin-approved date
            if selected_date_obj != today:
                if request.user.allowed_past_date != selected_date_obj:
                    messages.warning(request, f'You can only mark attendance for today ({today.strftime("%d-%m-%Y")}). Contact admin for permission.')
                    selected_date = str(today)
        except:
            selected_date = str(today)
    else:
        selected_date = request.GET.get('date', str(today))
    
    company_id = request.GET.get('company', '')
    
    # Get companies based on user role
    if request.user.is_supervisor():
        available_companies = request.user.assigned_companies.all()
    else:
        available_companies = Company.objects.all()
    
    # Get employees based on selected company and user access - OPTIMIZED
    employees = Employee.objects.filter(is_active=True).select_related('company').only(
        'id', 'employee_code', 'first_name', 'last_name', 'designation',
        'salary_per_day', 'ot_per_hour', 'company__id', 'company__name'
    )
    
    if request.user.is_supervisor():
        employees = employees.filter(company__in=available_companies)
    
    if company_id:
        employees = employees.filter(company_id=company_id)
    
    # Get existing attendance for the date
    existing_attendance = {}
    if selected_date:
        attendance_records = Attendance.objects.filter(date=selected_date)
        existing_attendance = {att.employee_id: att for att in attendance_records}
    
    # Handle POST request
    if request.method == 'POST':
        selected_date = request.POST.get('date')
        company_id = request.POST.get('company')
        
        # Validate date for supervisors
        if request.user.is_supervisor():
            try:
                selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
                if selected_date_obj != today and request.user.allowed_past_date != selected_date_obj:
                    messages.error(request, f'You can only mark attendance for today ({today.strftime("%d-%m-%Y")}). Contact admin for permission.')
                    return redirect('attendance:bulk_mark_attendance')
            except:
                messages.error(request, 'Invalid date.')
                return redirect('attendance:bulk_mark_attendance')
        
        count = 0
        
        # Re-filter employees for the POST
        post_employees = Employee.objects.filter(is_active=True)
        if request.user.is_supervisor():
            post_employees = post_employees.filter(company__in=available_companies)
        if company_id:
            post_employees = post_employees.filter(company_id=company_id)
        
        for employee in post_employees:
            status = request.POST.get(f'status_{employee.id}')
            has_ot = request.POST.get(f'has_ot_{employee.id}') == 'on'
            ot_hours = request.POST.get(f'ot_hours_{employee.id}', '0')
            remarks = request.POST.get(f'remarks_{employee.id}', '')
            
            if status:
                try:
                    ot_hours_decimal = Decimal(ot_hours) if ot_hours and has_ot else Decimal('0.00')
                except:
                    ot_hours_decimal = Decimal('0.00')
                
                # Update or create attendance
                attendance, created = Attendance.objects.update_or_create(
                    employee=employee,
                    date=selected_date,
                    defaults={
                        'status': status,
                        'has_ot': has_ot,
                        'ot_hours': ot_hours_decimal,
                        'remarks': remarks,
                        'marked_by': request.user
                    }
                )
                count += 1
        
        messages.success(request, f'Attendance marked for {count} employees')
        return redirect(f'attendance:bulk_mark_attendance')
    
    form = BulkAttendanceForm(
        initial={'date': selected_date, 'company': company_id},
        user=request.user
    )
    
    context = {
        'form': form,
        'employees': employees,
        'selected_date': selected_date,
        'selected_company': company_id,
        'existing_attendance': existing_attendance,
        'available_companies': available_companies,
    }
    return render(request, 'attendance/bulk_mark_attendance.html', context)


@login_required
def attendance_list(request):
    """List attendance records with filters"""
    # Get filter parameters and enforce 3-month restriction
    start_date_raw = request.GET.get('start_date', '')
    end_date_raw = request.GET.get('end_date', '')
    start_date, end_date = validate_date_range(start_date_raw, end_date_raw)
    
    employee_id = request.GET.get('employee', '')
    status = request.GET.get('status', '')
    company_id = request.GET.get('company', '')
    
    # Get min allowed date for template
    min_allowed_date = get_min_allowed_date().strftime('%Y-%m-%d')
    
    # Base queryset - always filter by 3-month range
    attendance_records = Attendance.objects.select_related(
        'employee', 'employee__company', 'marked_by'
    ).filter(
        date__gte=min_allowed_date
    )
    
    # Filter by supervisor access
    if request.user.is_supervisor():
        assigned_employees = request.user.get_assigned_employees()
        attendance_records = attendance_records.filter(employee__in=assigned_employees)
    
    # Apply filters
    if start_date:
        attendance_records = attendance_records.filter(date__gte=start_date)
    if end_date:
        attendance_records = attendance_records.filter(date__lte=end_date)
    if employee_id:
        attendance_records = attendance_records.filter(employee_id=employee_id)
    if status:
        attendance_records = attendance_records.filter(status=status)
    if company_id:
        attendance_records = attendance_records.filter(employee__company_id=company_id)
    
    # Order by date descending
    attendance_records = attendance_records.order_by('-date', 'employee__first_name')
    
    # Get data for filters
    if request.user.is_supervisor():
        employees = request.user.get_assigned_employees()
        companies = request.user.assigned_companies.all()
    else:
        employees = Employee.objects.filter(is_active=True)
        companies = Company.objects.all()
    
    context = {
        'attendance_records': attendance_records[:100],  # Limit for performance
        'employees': employees,
        'companies': companies,
        'start_date': start_date,
        'end_date': end_date,
        'min_allowed_date': min_allowed_date,
        'selected_employee': employee_id,
        'selected_status': status,
        'selected_company': company_id,
    }
    return render(request, 'attendance/attendance_list.html', context)


@login_required
@admin_required
def reports(request):
    """Generate attendance reports with salary calculations - Admin only"""
    # Get filter parameters and enforce 3-month restriction
    from_date_raw = request.GET.get('from_date', '')
    to_date_raw = request.GET.get('to_date', '')
    from_date, to_date = validate_date_range(from_date_raw, to_date_raw)
    
    company_id = request.GET.get('company', '')
    employee_id = request.GET.get('employee', '')
    
    # Get min allowed date for template
    min_allowed_date = get_min_allowed_date().strftime('%Y-%m-%d')
    
    # Base queryset
    attendance_records = Attendance.objects.select_related(
        'employee', 'employee__company', 'marked_by'
    ).filter(
        date__gte=from_date,
        date__lte=to_date
    ).order_by('employee', 'date')
    
    # Apply filters
    if company_id:
        attendance_records = attendance_records.filter(employee__company_id=company_id)
    if employee_id:
        attendance_records = attendance_records.filter(employee_id=employee_id)
    
    # Calculate detailed report data
    report_data = []
    total_salary = Decimal('0.00')
    total_ot = Decimal('0.00')
    total_grand = Decimal('0.00')
    
    for record in attendance_records:
        day_salary = record.day_salary
        ot_amount = record.ot_amount
        total_amount = record.total_amount
        
        report_data.append({
            'record': record,
            'day_salary': day_salary,
            'ot_amount': ot_amount,
            'total_amount': total_amount,
        })
        
        total_salary += day_salary
        total_ot += ot_amount
        total_grand += total_amount
    
    # Calculate summary statistics
    present_count = attendance_records.filter(status='PRESENT').count()
    absent_count = attendance_records.filter(status='ABSENT').count()
    ot_count = attendance_records.filter(has_ot=True).count()
    
    # Get data for filters
    companies = Company.objects.all()
    employees = Employee.objects.filter(is_active=True)
    
    context = {
        'report_data': report_data,
        'total_salary': total_salary,
        'total_ot': total_ot,
        'total_grand': total_grand,
        'present_count': present_count,
        'absent_count': absent_count,
        'ot_count': ot_count,
        'total_records': len(report_data),
        'companies': companies,
        'employees': employees,
        'from_date': from_date,
        'to_date': to_date,
        'min_allowed_date': min_allowed_date,
        'selected_company': company_id,
        'selected_employee': employee_id,
    }
    return render(request, 'attendance/reports.html', context)


@login_required
@admin_required
def export_report_csv(request):
    """Export attendance report to CSV with salary details"""
    # Enforce 3-month restriction
    from_date_raw = request.GET.get('from_date', '')
    to_date_raw = request.GET.get('to_date', '')
    from_date, to_date = validate_date_range(from_date_raw, to_date_raw)
    
    company_id = request.GET.get('company', '')
    employee_id = request.GET.get('employee', '')
    
    # Base queryset
    attendance_records = Attendance.objects.select_related(
        'employee', 'employee__company', 'marked_by'
    ).filter(
        date__gte=from_date,
        date__lte=to_date
    ).order_by('employee', 'date')
    
    if company_id:
        attendance_records = attendance_records.filter(employee__company_id=company_id)
    if employee_id:
        attendance_records = attendance_records.filter(employee_id=employee_id)
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="attendance_report_{from_date}_to_{to_date}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Date', 'Employee Code', 'Employee Name', 'Company', 
        'Status', 'OT', 'OT Hours', 'Day Rate', 'Day Salary', 
        'OT Rate', 'OT Amount', 'Total Amount', 'Marked By'
    ])
    
    total_salary = Decimal('0.00')
    total_ot = Decimal('0.00')
    total_grand = Decimal('0.00')
    
    for record in attendance_records:
        day_salary = record.day_salary
        ot_amount = record.ot_amount
        total_amount = record.total_amount
        
        total_salary += day_salary
        total_ot += ot_amount
        total_grand += total_amount
        
        writer.writerow([
            record.date,
            record.employee.employee_code,
            record.employee.get_full_name(),
            record.employee.company.name,
            record.get_status_display(),
            'Yes' if record.has_ot else 'No',
            record.ot_hours if record.has_ot else '',
            record.employee.salary_per_day,
            day_salary,
            record.employee.ot_per_hour,
            ot_amount,
            total_amount,
            record.marked_by.get_full_name() if record.marked_by else ''
        ])
    
    # Add totals row
    writer.writerow([])
    writer.writerow(['', '', '', '', '', '', '', 'TOTALS:', total_salary, '', total_ot, total_grand, ''])
    
    return response


@login_required
@admin_required  
def employee_wise_report(request):
    """Employee-wise summary report"""
    # Enforce 3-month restriction
    from_date_raw = request.GET.get('from_date', '')
    to_date_raw = request.GET.get('to_date', '')
    from_date, to_date = validate_date_range(from_date_raw, to_date_raw)
    
    company_id = request.GET.get('company', '')
    min_allowed_date = get_min_allowed_date().strftime('%Y-%m-%d')
    
    # Get employees
    employees = Employee.objects.filter(is_active=True).select_related('company')
    if company_id:
        employees = employees.filter(company_id=company_id)
    
    # Build summary for each employee
    employee_summary = []
    grand_total_salary = Decimal('0.00')
    grand_total_ot = Decimal('0.00')
    grand_total = Decimal('0.00')
    
    for emp in employees:
        records = Attendance.objects.filter(
            employee=emp,
            date__gte=from_date,
            date__lte=to_date
        )
        
        present_days = records.filter(status='PRESENT').count()
        absent_days = records.filter(status='ABSENT').count()
        ot_days = records.filter(has_ot=True).count()
        total_ot_hours = sum([r.ot_hours for r in records.filter(has_ot=True)])
        
        total_salary = present_days * emp.salary_per_day
        total_ot_amount = total_ot_hours * emp.ot_per_hour
        total_amount = total_salary + total_ot_amount
        
        employee_summary.append({
            'employee': emp,
            'present_days': present_days,
            'absent_days': absent_days,
            'ot_days': ot_days,
            'total_ot_hours': total_ot_hours,
            'total_salary': total_salary,
            'total_ot_amount': total_ot_amount,
            'total_amount': total_amount,
        })
        
        grand_total_salary += total_salary
        grand_total_ot += total_ot_amount
        grand_total += total_amount
    
    companies = Company.objects.all()
    
    context = {
        'employee_summary': employee_summary,
        'grand_total_salary': grand_total_salary,
        'grand_total_ot': grand_total_ot,
        'grand_total': grand_total,
        'companies': companies,
        'from_date': from_date,
        'to_date': to_date,
        'min_allowed_date': min_allowed_date,
        'selected_company': company_id,
    }
    return render(request, 'attendance/employee_wise_report.html', context)
