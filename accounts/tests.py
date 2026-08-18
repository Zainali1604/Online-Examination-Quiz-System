from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import StudentProfile, TeacherProfile

User = get_user_model()


class AccountsModelAndAuthTests(TestCase):
    def setUp(self):
        self.student_user = User.objects.create_user(
            username='student1',
            email='student1@college.edu',
            password='Password123!',
            role=User.Role.STUDENT
        )
        StudentProfile.objects.create(
            user=self.student_user,
            roll_number='CS-2026-01',
            department='Computer Science'
        )

        self.teacher_user = User.objects.create_user(
            username='teacher1',
            email='teacher1@college.edu',
            password='Password123!',
            role=User.Role.TEACHER
        )
        TeacherProfile.objects.create(
            user=self.teacher_user,
            employee_id='TCH-2026-01',
            department='Information Technology'
        )

    def test_user_roles(self):
        self.assertTrue(self.student_user.is_student)
        self.assertFalse(self.student_user.is_teacher)
        self.assertTrue(self.teacher_user.is_teacher)
        self.assertFalse(self.teacher_user.is_student)

    def test_student_registration_view(self):
        response = self.client.post(reverse('accounts:register') + '?role=student', {
            'username': 'newstudent',
            'email': 'newstudent@college.edu',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'roll_number': 'CS-2026-99',
            'department': 'Computer Science',
            'password': 'Password123!',
            'confirm_password': 'Password123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newstudent').exists())

    def test_login_and_role_redirect(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'teacher1',
            'password': 'Password123!'
        })
        self.assertRedirects(response, reverse('dashboard:teacher_dashboard'))

    def test_edit_profile_view_student(self):
        self.client.login(username='student1', password='Password123!')
        response = self.client.get(reverse('accounts:profile_edit'))
        self.assertEqual(response.status_code, 200)

        post_response = self.client.post(reverse('accounts:profile_edit'), {
            'username': 'hacked_name',
            'roll_number': 'HACK-999',
            'first_name': 'UpdatedFirst',
            'last_name': 'UpdatedLast',
            'email': 'updatedstudent@college.edu',
            'department': 'Software Engineering',
            'phone_number': '+9876543210'
        })
        self.assertRedirects(post_response, reverse('accounts:profile'))
        
        self.student_user.refresh_from_db()
        self.assertEqual(self.student_user.username, 'student1')
        self.assertEqual(self.student_user.student_profile.roll_number, 'CS-2026-01')
        self.assertEqual(self.student_user.first_name, 'UpdatedFirst')
        self.assertEqual(self.student_user.email, 'updatedstudent@college.edu')
        self.assertEqual(self.student_user.student_profile.department, 'Software Engineering')
        self.assertEqual(self.student_user.student_profile.phone_number, '+9876543210')

    def test_edit_profile_view_teacher(self):
        self.client.login(username='teacher1', password='Password123!')
        response = self.client.get(reverse('accounts:profile_edit'))
        self.assertEqual(response.status_code, 200)

        post_response = self.client.post(reverse('accounts:profile_edit'), {
            'username': 'hacked_teacher',
            'employee_id': 'TCH-HACK-999',
            'first_name': 'ProfFirst',
            'last_name': 'ProfLast',
            'email': 'updatedteacher@college.edu',
            'department': 'Data Science',
            'qualification': 'Ph.D. in CS',
            'phone_number': '+1122334455'
        })
        self.assertRedirects(post_response, reverse('accounts:profile'))

        self.teacher_user.refresh_from_db()
        self.assertEqual(self.teacher_user.username, 'teacher1')
        self.assertEqual(self.teacher_user.teacher_profile.employee_id, 'TCH-2026-01')
        self.assertEqual(self.teacher_user.first_name, 'ProfFirst')
        self.assertEqual(self.teacher_user.teacher_profile.department, 'Data Science')
        self.assertEqual(self.teacher_user.teacher_profile.qualification, 'Ph.D. in CS')




