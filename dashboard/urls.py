from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('performance/', views.performance_view, name='performance'),
]
