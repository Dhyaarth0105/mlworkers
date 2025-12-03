from django.db import models
from decimal import Decimal
from companies.models import Company


class Employee(models.Model):
    """Employee model for managing employee information"""
    
    employee_code = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='employees'
    )
    designation = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    date_of_joining = models.DateField()
    
    # Salary fields
    salary_per_day = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Daily salary amount"
    )
    ot_per_hour = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Overtime rate per hour"
    )
    
    # Additional identification fields
    uan_number = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        help_text="Universal Account Number (PF)"
    )
    gatepass_number = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        help_text="Gatepass/Access Card Number"
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'employees'
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.employee_code} - {self.get_full_name()}"
    
    def get_full_name(self):
        """Get employee's full name"""
        return f"{self.first_name} {self.last_name}"
    
    def get_attendance_count(self, month=None, year=None):
        """Get attendance count for a specific month/year"""
        from attendance.models import Attendance
        from datetime import date
        
        if month and year:
            return Attendance.objects.filter(
                employee=self,
                date__month=month,
                date__year=year
            ).count()
        return Attendance.objects.filter(employee=self).count()
