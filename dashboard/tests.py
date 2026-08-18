from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from exams.models import Exam

User = get_user_model()


class DashboardAnalyticsTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='dash_teacher',
            password='Password123!',
            role=User.Role.TEACHER
        )
        self.student = User.objects.create_user(
            username='dash_student',
            password='Password123!',
            role=User.Role.STUDENT
        )
        self.exam = Exam.objects.create(
            created_by=self.teacher,
            title='Dashboard Analytics Test Exam',
            is_published=True
        )

    def test_student_dashboard_access(self):
        self.client.login(username='dash_student', password='Password123!')
        response = self.client.get(reverse('dashboard:student_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('available_count', response.context)
        self.assertEqual(response.context['available_count'], 1)

    def test_teacher_dashboard_access(self):
        self.client.login(username='dash_teacher', password='Password123!')
        response = self.client.get(reverse('dashboard:teacher_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_exams', response.context)
        self.assertEqual(response.context['total_exams'], 1)
