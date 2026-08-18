from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from exams.models import Exam, Question, Option

User = get_user_model()


class ExamManagementTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher_test',
            password='Password123!',
            role=User.Role.TEACHER
        )
        self.student = User.objects.create_user(
            username='student_test',
            password='Password123!',
            role=User.Role.STUDENT
        )
        self.exam = Exam.objects.create(
            created_by=self.teacher,
            title='Python Programming 101',
            duration_minutes=30,
            total_marks=100,
            pass_marks=40
        )

    def test_create_exam_by_teacher(self):
        self.client.login(username='teacher_test', password='Password123!')
        response = self.client.post(reverse('exams:create_exam'), {
            'title': 'Database Management Systems',
            'description': 'SQL and Relational DBs',
            'duration_minutes': 45,
            'total_marks': 50,
            'pass_marks': 20,
            'is_published': False
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Exam.objects.filter(title='Database Management Systems').exists())

    def test_student_cannot_create_exam(self):
        self.client.login(username='student_test', password='Password123!')
        response = self.client.get(reverse('exams:create_exam'))
        self.assertEqual(response.status_code, 302)  # Blocked and redirected

    def test_add_question_with_options(self):
        self.client.login(username='teacher_test', password='Password123!')
        response = self.client.post(reverse('exams:add_question', args=[self.exam.id]), {
            'question_text': 'What is Django?',
            'marks': 5,
            'order': 1,
            'option_1': 'A Web Framework',
            'option_2': 'A Database',
            'option_3': 'An Operating System',
            'option_4': 'A Programming Language',
            'correct_option': '1'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.exam.question_count, 1)
        q = self.exam.questions.first()
        self.assertEqual(q.options.count(), 4)
        self.assertTrue(q.correct_option.option_text == 'A Web Framework')
