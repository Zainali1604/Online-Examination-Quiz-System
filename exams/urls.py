from django.urls import path
from . import views

app_name = 'exams'

urlpatterns = [
    path('', views.exam_list, name='exam_list'),
    path('<int:exam_id>/', views.exam_detail, name='exam_detail'),
    path('create/', views.create_exam, name='create_exam'),
    path('<int:exam_id>/edit/', views.edit_exam, name='edit_exam'),
    path('<int:exam_id>/delete/', views.delete_exam, name='delete_exam'),
    path('<int:exam_id>/toggle-publish/', views.toggle_publish_exam, name='toggle_publish'),
    path('<int:exam_id>/questions/', views.question_list, name='question_list'),
    path('<int:exam_id>/questions/add/', views.add_question, name='add_question'),
    path('questions/<int:question_id>/edit/', views.edit_question, name='edit_question'),
    path('questions/<int:question_id>/delete/', views.delete_question, name='delete_question'),
]
