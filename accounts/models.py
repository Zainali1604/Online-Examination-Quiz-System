from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom User model extending Django's built-in AbstractUser.
    Adds a 'role' field to easily distinguish between ADMIN, TEACHER, and STUDENT.
    """
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        TEACHER = 'TEACHER', 'Teacher'
        STUDENT = 'STUDENT', 'Student'

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT,
        help_text="Role of the user in the system"
    )

    @property
    def is_student(self):
        """Helper method to check if user is a student."""
        return self.role == self.Role.STUDENT

    @property
    def is_teacher(self):
        """Helper method to check if user is a teacher."""
        return self.role == self.Role.TEACHER or self.is_superuser

    @property
    def is_admin(self):
        """Helper method to check if user is an admin."""
        return self.role == self.Role.ADMIN or self.is_superuser

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class StudentProfile(models.Model):
    """
    Profile model for Students.
    Connected 1-to-1 with the custom User model.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    roll_number = models.CharField(max_length=30, unique=True, help_text="Unique Student Roll Number")
    department = models.CharField(max_length=100, help_text="Department (e.g., Computer Science)")
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics/students/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Student: {self.user.get_full_name() or self.user.username} ({self.roll_number})"


class TeacherProfile(models.Model):
    """
    Profile model for Teachers.
    Connected 1-to-1 with the custom User model.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='teacher_profile'
    )
    employee_id = models.CharField(max_length=30, unique=True, help_text="Unique Teacher Employee ID")
    department = models.CharField(max_length=100, help_text="Department (e.g., Information Technology)")
    qualification = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., M.Tech, Ph.D.")
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics/teachers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Teacher: {self.user.get_full_name() or self.user.username} ({self.employee_id})"
