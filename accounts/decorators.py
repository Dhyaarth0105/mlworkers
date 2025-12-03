from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    """Decorator to restrict access to admin users only"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_admin():
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('accounts:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def supervisor_required(view_func):
    """Decorator to restrict access to supervisor users only"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_supervisor():
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('accounts:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper
