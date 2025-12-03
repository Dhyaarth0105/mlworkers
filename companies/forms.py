from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
from .models import Company


class CompanyForm(forms.ModelForm):
    """Form for creating and editing companies"""
    
    class Meta:
        model = Company
        fields = ['name', 'address', 'contact_number', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Company Address'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('name'),
            Field('address'),
            Row(
                Column(Field('contact_number'), css_class='col-md-6'),
                Column(Field('email'), css_class='col-md-6'),
            ),
            Submit('submit', 'Save Company', css_class='btn btn-primary mt-3')
        )
