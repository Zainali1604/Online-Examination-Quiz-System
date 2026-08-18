from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from exams.models import Exam, Question, Option
from attempts.models import ExamAttempt, StudentAnswer, Result

User = get_user_model()


class ExamAttemptAndEvaluationTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='eval_teacher',
            password='Password123!',
            role=User.Role.TEACHER
        )
        self.student = User.objects.create_user(
            username='eval_student',
            password='Password123!',
            role=User.Role.STUDENT
        )
        self.exam = Exam.objects.create(
            created_by=self.teacher,
            title='Python Evaluation Test',
            duration_minutes=20,
            total_marks=10,
            pass_marks=5,
            is_published=True
        )

        # Question 1 (5 Marks)
        self.q1 = Question.objects.create(
            exam=self.exam,
            question_text='What is the keyword for defining a function in Python?',
            marks=5,
            order=1
        )
        self.q1_opt1 = Option.objects.create(question=self.q1, option_text='def', is_correct=True)
        self.q1_opt2 = Option.objects.create(question=self.q1, option_text='func', is_correct=False)

        # Question 2 (5 Marks)
        self.q2 = Question.objects.create(
            exam=self.exam,
            question_text='Which data type is immutable?',
            marks=5,
            order=2
        )
        self.q2_opt1 = Option.objects.create(question=self.q2, option_text='tuple', is_correct=True)
        self.q2_opt2 = Option.objects.create(question=self.q2, option_text='list', is_correct=False)

    def test_start_exam(self):
        self.client.login(username='eval_student', password='Password123!')
        response = self.client.get(reverse('attempts:start_exam', args=[self.exam.id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ExamAttempt.objects.filter(student=self.student, exam=self.exam).exists())

    def test_submit_and_automatic_evaluation(self):
        self.client.login(username='eval_student', password='Password123!')
        attempt = ExamAttempt.objects.create(
            student=self.student,
            exam=self.exam,
            total_questions=2,
            total_marks=10
        )

        # Submit Q1 correct, Q2 wrong
        response = self.client.post(reverse('attempts:submit_exam', args=[attempt.id]), {
            f'question_{self.q1.id}': self.q1_opt1.id,  # Correct (5 marks)
            f'question_{self.q2.id}': self.q2_opt2.id,  # Wrong (0 marks)
        })

        self.assertEqual(response.status_code, 302)
        attempt.refresh_from_db()
        self.assertTrue(attempt.is_completed)
        self.assertEqual(attempt.obtained_marks, 5.0)
        self.assertEqual(attempt.percentage, 50.0)
        self.assertEqual(attempt.status, ExamAttempt.Status.PASSED)
        self.assertTrue(Result.objects.filter(attempt=attempt).exists())
