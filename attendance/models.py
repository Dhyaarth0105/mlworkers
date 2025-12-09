from django.db import models
from django.conf import settings
from employees.models import Employee
from decimal import Decimal


class Attendance(models.Model):
    """Attendance model for tracking employee attendance"""
    
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('HALF_DAY', 'Half Day'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PRESENT')
    
    # OT as separate Yes/No field
    has_ot = models.BooleanField(default=False, help_text='Did employee work overtime?')
    ot_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Number of overtime hours'
    )
    ot_remarks = models.CharField(max_length=255, blank=True, null=True, help_text='OT remarks/reason')
    
    remarks = models.TextField(blank=True, null=True)
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='attendance_marked'
    )
    marked_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Track if attendance was edited
    is_edited = models.BooleanField(default=False)
    edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendance_edited'
    )
    edited_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'attendance'
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendance Records'
        ordering = ['-date', 'employee']
        unique_together = ['employee', 'date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['status']),
            models.Index(fields=['marked_by']),
            models.Index(fields=['-date', 'employee']),
        ]
    
    def __str__(self):
        ot_str = " + OT" if self.has_ot else ""
        return f"{self.employee.get_full_name()} - {self.date} - {self.get_status_display()}{ot_str}"
    
    def save(self, *args, **kwargs):
        # Clear OT hours if no OT
        if not self.has_ot:
            self.ot_hours = None
            self.ot_remarks = None
        super().save(*args, **kwargs)
    
    @property
    def day_salary(self):
        """Calculate day salary based on attendance"""
        if self.status == 'PRESENT':
            return self.employee.salary_per_day or Decimal('0.00')
        elif self.status == 'HALF_DAY':
            salary = self.employee.salary_per_day or Decimal('0.00')
            return salary / 2
        return Decimal('0.00')
    
    @property
    def ot_amount(self):
        """Calculate OT amount"""
        if self.has_ot and self.ot_hours:
            ot_rate = self.employee.ot_per_hour or Decimal('0.00')
            return self.ot_hours * ot_rate
        return Decimal('0.00')
    
    @property
    def total_amount(self):
        """Calculate total amount (day salary + OT)"""
        return self.day_salary + self.ot_amount
