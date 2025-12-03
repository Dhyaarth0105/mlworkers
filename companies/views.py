from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from accounts.decorators import admin_required
from .models import Company
from .forms import CompanyForm


@admin_required
def company_list(request):
    """List all companies with search functionality"""
    query = request.GET.get('q', '')
    companies = Company.objects.all()
    
    if query:
        companies = companies.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(contact_number__icontains=query)
        )
    
    context = {
        'companies': companies,
        'query': query,
    }
    return render(request, 'companies/company_list.html', context)


@admin_required
def company_create(request):
    """Create a new company"""
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            company = form.save(commit=False)
            company.created_by = request.user
            company.save()
            messages.success(request, f'Company "{company.name}" created successfully!')
            return redirect('companies:company_list')
    else:
        form = CompanyForm()
    
    context = {'form': form, 'title': 'Add New Company'}
    return render(request, 'companies/company_form.html', context)


@admin_required
def company_detail(request, pk):
    """View company details"""
    company = get_object_or_404(Company, pk=pk)
    employees = company.employees.filter(is_active=True)
    
    context = {
        'company': company,
        'employees': employees,
    }
    return render(request, 'companies/company_detail.html', context)


@admin_required
def company_update(request, pk):
    """Update company information"""
    company = get_object_or_404(Company, pk=pk)
    
    if request.method == 'POST':
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, f'Company "{company.name}" updated successfully!')
            return redirect('companies:company_detail', pk=company.pk)
    else:
        form = CompanyForm(instance=company)
    
    context = {
        'form': form,
        'title': f'Edit {company.name}',
        'company': company
    }
    return render(request, 'companies/company_form.html', context)


@admin_required
def company_delete(request, pk):
    """Delete a company"""
    company = get_object_or_404(Company, pk=pk)
    
    if request.method == 'POST':
        company_name = company.name
        company.delete()
        messages.success(request, f'Company "{company_name}" deleted successfully!')
        return redirect('companies:company_list')
    
    context = {'company': company}
    return render(request, 'companies/company_confirm_delete.html', context)
