from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

User = get_user_model()

phone_validator = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Enter a valid mobile number (9-15 digits)"
)


class LoginForm(AuthenticationForm):
    """Custom login form with Bootstrap styling"""
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Username or Email',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Password'
        })
    )


class SignupForm(forms.ModelForm):
    """User registration form"""
    
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'First Name',
            'autofocus': True
        })
    )
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Last Name'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Email Address'
        })
    )
    mobile = forms.CharField(
        max_length=15,
        validators=[phone_validator],
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Mobile Number',
            'type': 'tel'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Password'
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Confirm Password'
        })
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'mobile']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email
    
    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if User.objects.filter(mobile=mobile).exists():
            raise forms.ValidationError("This mobile number is already registered.")
        return mobile
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # Use email as username
        user.set_password(self.cleaned_data['password'])
        user.role = 'SUPERVISOR'  # Default role for new users
        if commit:
            user.save()
        return user


class ForgotPasswordForm(forms.Form):
    """Form to request password reset OTP"""
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your registered email',
            'autofocus': True
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("No account found with this email address.")
        return email


class VerifyOTPForm(forms.Form):
    """Form to verify OTP"""
    
    otp = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg text-center otp-input',
            'placeholder': '------',
            'maxlength': '6',
            'autofocus': True,
            'autocomplete': 'off',
            'inputmode': 'numeric',
            'pattern': '[0-9]*'
        })
    )


class ResetPasswordForm(forms.Form):
    """Form to reset password after OTP verification"""
    
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'New Password',
            'autofocus': True
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Confirm New Password'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        
        if new_password and len(new_password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        
        return cleaned_data


class UserManagementForm(forms.ModelForm):
    """Form for admin to create/edit users (supervisors, admins)"""
    
    from companies.models import Company
    
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password (leave blank to keep current)'
        }),
        help_text='Leave blank to keep existing password when editing'
    )
    
    confirm_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'mobile', 'role', 'assigned_companies', 'allowed_past_date', 'is_active']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'assigned_companies': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'size': '5'
            }),
            'allowed_past_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_companies'].required = False
        self.fields['assigned_companies'].help_text = 'Hold Ctrl/Cmd to select multiple companies (for Supervisors)'
        self.fields['allowed_past_date'].required = False
        self.fields['allowed_past_date'].help_text = 'Allow supervisor to mark attendance for this specific past date (optional)'
        
        # Make password required for new users
        if not self.instance.pk:
            self.fields['password'].required = True
            self.fields['confirm_password'].required = True
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("This email is already registered.")
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password or confirm_password:
            if password != confirm_password:
                raise forms.ValidationError("Passwords do not match.")
            if password and len(password) < 6:
                raise forms.ValidationError("Password must be at least 6 characters long.")
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        
        if commit:
            user.save()
            self.save_m2m()  # Save many-to-many relationships
        return user
