from django.urls import path
from . import views

app_name = 'attempts'

urlpatterns = [
    path('start/<int:exam_id>/', views.start_exam, name='start_exam'),
    path('<int:attempt_id>/', views.attempt_exam, name='attempt_exam'),
    path('<int:attempt_id>/submit/', views.submit_exam, name='submit_exam'),
    path('<int:attempt_id>/result/', views.result_view, name='result'),
    path('<int:attempt_id>/review/', views.answer_review, name='answer_review'),
    path('history/', views.attempt_history, name='attempt_history'),
]
