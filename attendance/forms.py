from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, HTML
from .models import Attendance
from datetime import date


class AttendanceForm(forms.ModelForm):
    """Form for marking single attendance"""
    
    class Meta:
        model = Attendance
        fields = ['employee', 'date', 'status', 'has_ot', 'ot_hours', 'ot_remarks', 'remarks']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'has_ot': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ot_hours': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.5', 
                'placeholder': 'Enter OT Hours',
                'min': '0',
            }),
            'ot_remarks': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'OT Remarks/Reason (Optional)'
            }),
            'remarks': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 2, 
                'placeholder': 'Remarks (Optional)'
            }),
        }
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        from employees.models import Employee
        
        self.user = user
        
        # Make OT hours not required
        self.fields['ot_hours'].required = False
        
        # Filter employees based on user role
        if user and user.is_supervisor():
            self.fields['employee'].queryset = user.get_assigned_employees()
        else:
            self.fields['employee'].queryset = Employee.objects.filter(is_active=True)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        # Set OT hours to empty by default (no 0.00)
        self.fields['ot_hours'].initial = None
        self.fields['ot_remarks'].required = False
        
        # Update labels for cleaner display
        self.fields['has_ot'].label = 'Has OT?'
        self.fields['ot_hours'].label = 'OT Hours'
        self.fields['ot_remarks'].label = 'OT Remarks'
        
        self.helper.layout = Layout(
            Row(
                Column(Field('employee'), css_class='col-md-6'),
                Column(Field('date'), css_class='col-md-6'),
            ),
            Row(
                Column(Field('status', css_class='status-select'), css_class='col-md-12'),
            ),
            HTML('<div id="ot-section" style="display:none;">'),
            Row(
                Column(Field('has_ot'), css_class='col-md-3'),
                Column(Field('ot_hours'), css_class='col-md-4'),
                Column(Field('ot_remarks'), css_class='col-md-5'),
            ),
            HTML('</div>'),
            Field('remarks'),
            Submit('submit', 'Mark Attendance', css_class='btn btn-primary mt-3')
        )
    
    def clean_date(self):
        """Validate date - supervisors can only mark today unless given permission"""
        selected_date = self.cleaned_data.get('date')
        today = date.today()
        
        if self.user and self.user.is_supervisor():
            # Check if it's today
            if selected_date == today:
                return selected_date
            
            # Check if admin has granted permission for this specific date
            if self.user.allowed_past_date == selected_date:
                return selected_date
            
            # Otherwise, restrict to today only
            raise forms.ValidationError(
                f'You can only mark attendance for today ({today.strftime("%d-%m-%Y")}). '
                'Contact admin for permission to mark attendance for past dates.'
            )
        
        return selected_date
    
    def clean(self):
        cleaned_data = super().clean()
        has_ot = cleaned_data.get('has_ot')
        ot_hours = cleaned_data.get('ot_hours')
        
        # OT hours is optional - user enters the value, no default
        # Clear OT hours if no OT checkbox
        if not has_ot:
            cleaned_data['ot_hours'] = None
        
        return cleaned_data


class BulkAttendanceForm(forms.Form):
    """Form for selecting date and company for bulk attendance"""
    
    date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    company = forms.ModelChoiceField(
        queryset=None,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label='-- Select Company --'
    )
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        from companies.models import Company
        
        self.user = user
        
        if user and user.is_supervisor():
            self.fields['company'].queryset = user.assigned_companies.all()
        else:
            self.fields['company'].queryset = Company.objects.all()
    
    def clean_date(self):
        """Validate date - supervisors can only mark today unless given permission"""
        selected_date = self.cleaned_data.get('date')
        today = date.today()
        
        if self.user and self.user.is_supervisor():
            # Check if it's today
            if selected_date == today:
                return selected_date
            
            # Check if admin has granted permission for this specific date
            if self.user.allowed_past_date == selected_date:
                return selected_date
            
            # Otherwise, restrict to today only
            raise forms.ValidationError(
                f'You can only mark attendance for today ({today.strftime("%d-%m-%Y")}). '
                'Contact admin for permission to mark attendance for past dates.'
            )
        
        return selected_date


class AttendanceReportFilterForm(forms.Form):
    """Form for filtering attendance reports"""
    
    from_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    to_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    company = forms.ModelChoiceField(
        queryset=None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label='All Companies'
    )
    employee = forms.ModelChoiceField(
        queryset=None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label='All Employees'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from companies.models import Company
        from employees.models import Employee
        
        self.fields['company'].queryset = Company.objects.all()
        self.fields['employee'].queryset = Employee.objects.filter(is_active=True)
