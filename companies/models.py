from django.db import models
from django.conf import settings


class Company(models.Model):
    """Company model for managing company information"""
    
    name = models.CharField(max_length=200)
    address = models.TextField()
    contact_number = models.CharField(max_length=20)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='companies_created'
    )
    
    class Meta:
        db_table = 'companies'
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_employee_count(self):
        """Get total number of employees in this company"""
        return self.employees.filter(is_active=True).count()
