from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db.models import Q
from .forms import LoginForm, SignupForm, ForgotPasswordForm, VerifyOTPForm, ResetPasswordForm, UserManagementForm
from .models import PasswordResetOTP
from .decorators import admin_required

User = get_user_model()


def user_login(request):
    """Handle user login"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            
            # Redirect based on role
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('accounts:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def user_signup(request):
    """Handle user registration"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Account created successfully! Welcome, {user.first_name}!')
            login(request, user)
            return redirect('accounts:dashboard')
    else:
        form = SignupForm()
    
    return render(request, 'accounts/signup.html', {'form': form})


def forgot_password(request):
    """Handle forgot password - send OTP"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)
            
            # Invalidate any existing OTPs
            PasswordResetOTP.objects.filter(user=user, is_used=False).update(is_used=True)
            
            # Generate new OTP
            otp_code = PasswordResetOTP.generate_otp()
            PasswordResetOTP.objects.create(user=user, otp=otp_code)
            
            # Send email with OTP
            subject = 'Password Reset OTP - Attendance System'
            html_message = render_to_string('accounts/email/otp_email.html', {
                'user': user,
                'otp': otp_code,
                'expiry_minutes': settings.OTP_EXPIRY_MINUTES
            })
            plain_message = strip_tags(html_message)
            
            try:
                send_mail(
                    subject,
                    plain_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    html_message=html_message,
                    fail_silently=False,
                )
                messages.success(request, f'OTP sent to {email}. Please check your inbox.')
                request.session['reset_email'] = email
                return redirect('accounts:verify_otp')
            except Exception as e:
                messages.error(request, f'Failed to send email. Please try again later.')
    else:
        form = ForgotPasswordForm()
    
    return render(request, 'accounts/forgot_password.html', {'form': form})


def verify_otp(request):
    """Verify OTP for password reset"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    email = request.session.get('reset_email')
    if not email:
        messages.error(request, 'Please request a password reset first.')
        return redirect('accounts:forgot_password')
    
    if request.method == 'POST':
        form = VerifyOTPForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            
            try:
                user = User.objects.get(email=email)
                otp_record = PasswordResetOTP.objects.filter(
                    user=user,
                    otp=otp,
                    is_used=False
                ).latest('created_at')
                
                if otp_record.is_valid():
                    request.session['otp_verified'] = True
                    request.session['otp_id'] = otp_record.id
                    messages.success(request, 'OTP verified! Please set your new password.')
                    return redirect('accounts:reset_password')
                else:
                    messages.error(request, 'OTP has expired. Please request a new one.')
            except PasswordResetOTP.DoesNotExist:
                messages.error(request, 'Invalid OTP. Please try again.')
            except User.DoesNotExist:
                messages.error(request, 'User not found.')
    else:
        form = VerifyOTPForm()
    
    return render(request, 'accounts/verify_otp.html', {'form': form, 'email': email})


def reset_password(request):
    """Reset password after OTP verification"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    email = request.session.get('reset_email')
    otp_verified = request.session.get('otp_verified')
    otp_id = request.session.get('otp_id')
    
    if not email or not otp_verified or not otp_id:
        messages.error(request, 'Please verify your OTP first.')
        return redirect('accounts:forgot_password')
    
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.get(email=email)
                otp_record = PasswordResetOTP.objects.get(id=otp_id)
                
                # Set new password
                user.set_password(form.cleaned_data['new_password'])
                user.save()
                
                # Mark OTP as used
                otp_record.is_used = True
                otp_record.save()
                
                # Clear session data
                del request.session['reset_email']
                del request.session['otp_verified']
                del request.session['otp_id']
                
                messages.success(request, 'Password reset successfully! Please login with your new password.')
                return redirect('accounts:login')
            except (User.DoesNotExist, PasswordResetOTP.DoesNotExist):
                messages.error(request, 'An error occurred. Please try again.')
                return redirect('accounts:forgot_password')
    else:
        form = ResetPasswordForm()
    
    return render(request, 'accounts/reset_password.html', {'form': form})


def resend_otp(request):
    """Resend OTP"""
    email = request.session.get('reset_email')
    if not email:
        messages.error(request, 'Please request a password reset first.')
        return redirect('accounts:forgot_password')
    
    try:
        user = User.objects.get(email=email)
        
        # Invalidate existing OTPs
        PasswordResetOTP.objects.filter(user=user, is_used=False).update(is_used=True)
        
        # Generate new OTP
        otp_code = PasswordResetOTP.generate_otp()
        PasswordResetOTP.objects.create(user=user, otp=otp_code)
        
        # Send email
        subject = 'Password Reset OTP - Attendance System'
        html_message = render_to_string('accounts/email/otp_email.html', {
            'user': user,
            'otp': otp_code,
            'expiry_minutes': settings.OTP_EXPIRY_MINUTES
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            html_message=html_message,
            fail_silently=False,
        )
        messages.success(request, f'New OTP sent to {email}.')
    except Exception as e:
        messages.error(request, 'Failed to send OTP. Please try again.')
    
    return redirect('accounts:verify_otp')


@login_required
def user_logout(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


@login_required
def dashboard(request):
    """Dashboard view - redirects based on user role"""
    if request.user.is_admin():
        return redirect('accounts:admin_dashboard')
    else:
        return redirect('accounts:supervisor_dashboard')


@login_required
def admin_dashboard(request):
    """Admin dashboard with statistics"""
    from companies.models import Company
    from employees.models import Employee
    from attendance.models import Attendance
    from django.db.models import Count, Q
    from datetime import date
    
    # Get statistics
    total_companies = Company.objects.count()
    total_employees = Employee.objects.filter(is_active=True).count()
    today_attendance = Attendance.objects.filter(date=date.today()).count()
    
    # Recent companies
    recent_companies = Company.objects.order_by('-created_at')[:5]
    
    # Recent employees
    recent_employees = Employee.objects.order_by('-created_at')[:5]
    
    context = {
        'total_companies': total_companies,
        'total_employees': total_employees,
        'today_attendance': today_attendance,
        'recent_companies': recent_companies,
        'recent_employees': recent_employees,
    }
    
    return render(request, 'accounts/admin_dashboard.html', context)


@login_required
def supervisor_dashboard(request):
    """Supervisor dashboard"""
    from employees.models import Employee
    from attendance.models import Attendance
    from datetime import date
    
    # Get assigned companies and employees for supervisor
    assigned_companies = request.user.assigned_companies.all()
    assigned_employees = request.user.get_assigned_employees()
    
    # Get today's attendance count for assigned employees
    today_attendance = Attendance.objects.filter(
        date=date.today(),
        employee__in=assigned_employees
    ).count()
    
    # Get total assigned employees
    total_employees = assigned_employees.count()
    
    # Get recent attendance records marked by this supervisor
    recent_attendance = Attendance.objects.filter(
        marked_by=request.user
    ).select_related('employee', 'employee__company').order_by('-marked_at')[:10]
    
    context = {
        'today_attendance': today_attendance,
        'total_employees': total_employees,
        'assigned_companies': assigned_companies,
        'recent_attendance': recent_attendance,
    }
    
    return render(request, 'accounts/supervisor_dashboard.html', context)


# ==================== User Management Views (Admin Only) ====================

@login_required
@admin_required
def user_list(request):
    """List all users"""
    users = User.objects.all().order_by('-date_joined')
    
    # Filter by role
    role = request.GET.get('role')
    if role:
        users = users.filter(role=role)
    
    # Search
    search = request.GET.get('q')
    if search:
        users = users.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )
    
    context = {
        'users': users,
        'selected_role': role,
        'search_query': search,
    }
    return render(request, 'accounts/user_list.html', context)


@login_required
@admin_required
def user_create(request):
    """Create new user"""
    if request.method == 'POST':
        form = UserManagementForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User "{user.get_full_name()}" created successfully!')
            return redirect('accounts:user_list')
    else:
        form = UserManagementForm()
    
    return render(request, 'accounts/user_form.html', {
        'form': form,
        'title': 'Add New User',
        'button_text': 'Create User'
    })


@login_required
@admin_required
def user_edit(request, pk):
    """Edit existing user"""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        form = UserManagementForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'User "{user.get_full_name()}" updated successfully!')
            return redirect('accounts:user_list')
    else:
        form = UserManagementForm(instance=user)
    
    return render(request, 'accounts/user_form.html', {
        'form': form,
        'user_obj': user,
        'title': f'Edit User: {user.get_full_name()}',
        'button_text': 'Update User'
    })


@login_required
@admin_required
def user_delete(request, pk):
    """Delete user"""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        if user == request.user:
            messages.error(request, "You cannot delete your own account!")
        else:
            name = user.get_full_name()
            user.delete()
            messages.success(request, f'User "{name}" deleted successfully!')
        return redirect('accounts:user_list')
    
    return render(request, 'accounts/user_confirm_delete.html', {'user_obj': user})
