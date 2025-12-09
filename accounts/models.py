from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import random
import string


class User(AbstractUser):
    """Custom User model with role-based access"""
    
    ROLE_CHOICES = [
        ('SUPERADMIN', 'Super Admin'),
        ('ADMIN', 'Admin'),
        ('SUPERVISOR', 'Supervisor'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='SUPERVISOR'
    )
    mobile = models.CharField(max_length=15, blank=True, null=True)
    whatsapp_number = models.CharField(max_length=15, blank=True, null=True, help_text='WhatsApp number for notifications')
    
    # For supervisors and admins - which companies they can manage
    assigned_companies = models.ManyToManyField(
        'companies.Company',
        blank=True,
        related_name='assigned_users',
        help_text='Companies this user can manage (for admin/supervisor)'
    )
    
    # Permission to mark attendance for past dates (admin grants this)
    allowed_past_date = models.DateField(
        null=True, 
        blank=True,
        help_text='Specific past date supervisor is allowed to mark attendance for'
    )
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_superadmin(self):
        """Check if user is a superadmin"""
        return self.role == 'SUPERADMIN'
    
    def is_admin(self):
        """Check if user is an admin (includes superadmin)"""
        return self.role in ['ADMIN', 'SUPERADMIN']
    
    def is_supervisor(self):
        """Check if user is a supervisor"""
        return self.role == 'SUPERVISOR'
    
    def is_normal_admin(self):
        """Check if user is a normal admin (not superadmin)"""
        return self.role == 'ADMIN'
    
    def can_delete_user(self, target_user):
        """Check if this user can delete target user"""
        # Only superadmin can delete admins
        if target_user.is_superadmin():
            return False  # Nobody can delete superadmin
        if target_user.is_normal_admin():
            return self.is_superadmin()  # Only superadmin can delete admin
        return self.is_admin()  # Admin/superadmin can delete supervisors
    
    def can_edit_attendance(self):
        """Check if user can edit existing attendance"""
        return self.is_admin()  # Only admin/superadmin can edit
    
    def can_mark_any_date(self):
        """Check if user can mark attendance for any date"""
        return self.is_superadmin()  # Only superadmin has no date restrictions
    
    def get_full_name(self):
        """Return full name or username"""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.username
    
    def get_assigned_employees(self):
        """Get all employees from assigned companies"""
        from employees.models import Employee
        if self.is_superadmin():
            return Employee.objects.filter(is_active=True)
        if self.is_normal_admin() and self.assigned_companies.exists():
            return Employee.objects.filter(
                company__in=self.assigned_companies.all(),
                is_active=True
            )
        if self.is_normal_admin():
            return Employee.objects.filter(is_active=True)
        return Employee.objects.filter(
            company__in=self.assigned_companies.all(),
            is_active=True
        )
    
    def get_assigned_companies_for_view(self):
        """Get companies this user can view"""
        from companies.models import Company
        if self.is_superadmin():
            return Company.objects.all()
        if self.assigned_companies.exists():
            return self.assigned_companies.all()
        if self.is_normal_admin():
            return Company.objects.all()
        return self.assigned_companies.all()


class PasswordResetOTP(models.Model):
    """Store OTP for password reset"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_otps')
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'password_reset_otp'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"OTP for {self.user.email} - {self.otp}"
    
    @classmethod
    def generate_otp(cls):
        """Generate a 6-digit OTP"""
        return ''.join(random.choices(string.digits, k=6))
    
    def is_valid(self):
        """Check if OTP is still valid (within 10 minutes)"""
        from django.conf import settings
        expiry_minutes = getattr(settings, 'OTP_EXPIRY_MINUTES', 10)
        expiry_time = self.created_at + timezone.timedelta(minutes=expiry_minutes)
        return timezone.now() <= expiry_time and not self.is_used
