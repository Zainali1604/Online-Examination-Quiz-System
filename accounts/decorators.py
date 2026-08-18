from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin


def student_required(view_func):
    """
    Decorator for views that checks that the user is logged in and is a Student.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to access this page.")
            return redirect('accounts:login')
        if not request.user.is_student:
            messages.error(request, "Access denied. Student privileges required.")
            return redirect('dashboard:teacher_dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def teacher_required(view_func):
    """
    Decorator for views that checks that the user is logged in and is a Teacher/Admin.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to access this page.")
            return redirect('accounts:login')
        if not request.user.is_teacher:
            messages.error(request, "Access denied. Teacher privileges required.")
            return redirect('dashboard:student_dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


class StudentRequiredMixin(AccessMixin):
    """CBV Mixin to enforce Student role."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_student:
            messages.error(request, "Access denied. Student privileges required.")
            return redirect('dashboard:teacher_dashboard')
        return super().dispatch(request, *args, **kwargs)


class TeacherRequiredMixin(AccessMixin):
    """CBV Mixin to enforce Teacher role."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_teacher:
            messages.error(request, "Access denied. Teacher privileges required.")
            return redirect('dashboard:student_dashboard')
        return super().dispatch(request, *args, **kwargs)
