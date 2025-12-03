from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, HTML
from .models import Employee


class EmployeeForm(forms.ModelForm):
    """Form for creating and editing employees"""
    
    class Meta:
        model = Employee
        fields = ['employee_code', 'first_name', 'last_name', 'company', 
                  'designation', 'contact_number', 'email', 'date_of_joining',
                  'salary_per_day', 'ot_per_hour', 'uan_number', 'gatepass_number', 'is_active']
        widgets = {
            'employee_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Employee Code'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'company': forms.Select(attrs={'class': 'form-control'}),
            'designation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Designation'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email (Optional)'}),
            'date_of_joining': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'salary_per_day': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01', 'min': '0'}),
            'ot_per_hour': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01', 'min': '0'}),
            'uan_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'UAN Number (Optional)'}),
            'gatepass_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Gatepass Number (Optional)'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column(Field('employee_code'), css_class='col-md-6'),
                Column(Field('company'), css_class='col-md-6'),
            ),
            Row(
                Column(Field('first_name'), css_class='col-md-6'),
                Column(Field('last_name'), css_class='col-md-6'),
            ),
            Row(
                Column(Field('designation'), css_class='col-md-6'),
                Column(Field('date_of_joining'), css_class='col-md-6'),
            ),
            Row(
                Column(Field('contact_number'), css_class='col-md-6'),
                Column(Field('email'), css_class='col-md-6'),
            ),
            HTML('<hr class="my-4"><h5 class="mb-3"><i class="bi bi-currency-rupee"></i> Salary Details</h5>'),
            Row(
                Column(Field('salary_per_day'), css_class='col-md-6'),
                Column(Field('ot_per_hour'), css_class='col-md-6'),
            ),
            HTML('<hr class="my-4"><h5 class="mb-3"><i class="bi bi-card-text"></i> Identification Details</h5>'),
            Row(
                Column(Field('uan_number'), css_class='col-md-6'),
                Column(Field('gatepass_number'), css_class='col-md-6'),
            ),
            Field('is_active'),
            Submit('submit', 'Save Employee', css_class='btn btn-primary mt-3')
        )
