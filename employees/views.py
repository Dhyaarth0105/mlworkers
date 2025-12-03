from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from accounts.decorators import admin_required
from .models import Employee
from .forms import EmployeeForm


@admin_required
def employee_list(request):
    """List all employees with search and filter functionality"""
    query = request.GET.get('q', '')
    company_id = request.GET.get('company', '')
    status = request.GET.get('status', '')
    
    employees = Employee.objects.select_related('company').all()
    
    if query:
        employees = employees.filter(
            Q(employee_code__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(designation__icontains=query)
        )
    
    if company_id:
        employees = employees.filter(company_id=company_id)
    
    if status == 'active':
        employees = employees.filter(is_active=True)
    elif status == 'inactive':
        employees = employees.filter(is_active=False)
    
    from companies.models import Company
    companies = Company.objects.all()
    
    context = {
        'employees': employees,
        'companies': companies,
        'query': query,
        'selected_company': company_id,
        'selected_status': status,
    }
    return render(request, 'employees/employee_list.html', context)


@admin_required
def employee_create(request):
    """Create a new employee"""
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save()
            messages.success(request, f'Employee "{employee.get_full_name()}" created successfully!')
            return redirect('employees:employee_list')
    else:
        form = EmployeeForm()
    
    context = {'form': form, 'title': 'Add New Employee'}
    return render(request, 'employees/employee_form.html', context)


@admin_required
def employee_detail(request, pk):
    """View employee details"""
    employee = get_object_or_404(Employee, pk=pk)
    
    # Get recent attendance records
    from attendance.models import Attendance
    recent_attendance = Attendance.objects.filter(employee=employee).order_by('-date')[:10]
    
    context = {
        'employee': employee,
        'recent_attendance': recent_attendance,
    }
    return render(request, 'employees/employee_detail.html', context)


@admin_required
def employee_update(request, pk):
    """Update employee information"""
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, f'Employee "{employee.get_full_name()}" updated successfully!')
            return redirect('employees:employee_detail', pk=employee.pk)
    else:
        form = EmployeeForm(instance=employee)
    
    context = {
        'form': form,
        'title': f'Edit {employee.get_full_name()}',
        'employee': employee
    }
    return render(request, 'employees/employee_form.html', context)


@admin_required
def employee_delete(request, pk):
    """Delete an employee"""
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        employee_name = employee.get_full_name()
        employee.delete()
        messages.success(request, f'Employee "{employee_name}" deleted successfully!')
        return redirect('employees:employee_list')
    
    context = {'employee': employee}
    return render(request, 'employees/employee_confirm_delete.html', context)
