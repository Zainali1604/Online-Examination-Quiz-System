from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import (
    StudentRegistrationForm, TeacherRegistrationForm, UserLoginForm,
    UserUpdateForm, StudentProfileUpdateForm, TeacherProfileUpdateForm
)


def register_view(request):
    """
    Handles registration for both Students and Teachers.
    Uses 'role' GET parameter to switch active registration form.
    """
    if request.user.is_authenticated:
        if request.user.is_teacher:
            return redirect('dashboard:teacher_dashboard')
        return redirect('dashboard:student_dashboard')

    role = request.GET.get('role', 'student')
    
    if request.method == 'POST':
        if role == 'teacher':
            form = TeacherRegistrationForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                messages.success(request, f"Welcome Prof. {user.get_full_name() or user.username}! Account created successfully.")
                return redirect('dashboard:teacher_dashboard')
            student_form = StudentRegistrationForm()
            teacher_form = form
        else:
            form = StudentRegistrationForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                messages.success(request, f"Welcome {user.get_full_name() or user.username}! Account created successfully.")
                return redirect('dashboard:student_dashboard')
            student_form = form
            teacher_form = TeacherRegistrationForm()
    else:
        student_form = StudentRegistrationForm()
        teacher_form = TeacherRegistrationForm()

    context = {
        'role': role,
        'student_form': student_form,
        'teacher_form': teacher_form,
    }
    return render(request, 'accounts/register.html', context)


def login_view(request):
    """
    Handles authentication and role-based redirect for Students and Teachers.
    """
    if request.user.is_authenticated:
        if request.user.is_teacher:
            return redirect('dashboard:teacher_dashboard')
        return redirect('dashboard:student_dashboard')

    requested_role = request.GET.get('role')
    active_tab = requested_role if requested_role in ('student', 'teacher') else 'student'

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_active:
                    if requested_role == 'teacher' and not (user.is_teacher or user.is_superuser):
                        messages.error(request, "This account is registered as a Student. Please select the 'Student Login' tab.")
                    elif requested_role == 'student' and not (user.is_student or user.is_superuser):
                        messages.error(request, "This account is registered as a Teacher. Please select the 'Teacher Login' tab.")
                    else:
                        login(request, user)
                        messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
                        
                        next_url = request.GET.get('next')
                        if next_url:
                            return redirect(next_url)
                        
                        if user.is_teacher:
                            return redirect('dashboard:teacher_dashboard')
                        return redirect('dashboard:student_dashboard')
                else:
                    messages.error(request, "Your account is disabled. Please contact system admin.")
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {
        'form': form,
        'role': active_tab,
    })


@login_required
def logout_view(request):
    """
    Logs out the user and redirects to home page.
    """
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('home')


@login_required
def profile_view(request):
    """
    Renders user profile details depending on user role.
    """
    user = request.user
    profile = None
    if user.is_student and hasattr(user, 'student_profile'):
        profile = user.student_profile
    elif user.is_teacher and hasattr(user, 'teacher_profile'):
        profile = user.teacher_profile

    context = {
        'user': user,
        'profile': profile,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def profile_edit_view(request):
    """
    Handles updating user and role profile details.
    """
    user = request.user
    profile = None
    profile_form_class = None

    if user.is_student and hasattr(user, 'student_profile'):
        profile = user.student_profile
        profile_form_class = StudentProfileUpdateForm
    elif user.is_teacher and hasattr(user, 'teacher_profile'):
        profile = user.teacher_profile
        profile_form_class = TeacherProfileUpdateForm

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = profile_form_class(request.POST, instance=profile) if profile_form_class and profile else None

        user_valid = user_form.is_valid()
        profile_valid = profile_form.is_valid() if profile_form else True

        if user_valid and profile_valid:
            user_form.save()
            if profile_form:
                profile_form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('accounts:profile')
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = profile_form_class(instance=profile) if profile_form_class and profile else None

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile,
    }
    return render(request, 'accounts/profile_edit.html', context)

