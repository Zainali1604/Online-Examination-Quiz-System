from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from exams.models import Exam, Question, Option


class ExamAttempt(models.Model):
    """
    Represents a student's attempt for a specific Exam.
    Track timing, score calculations, and status.
    """
    class Status(models.TextChoices):
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        PASSED = 'PASSED', 'Passed'
        FAILED = 'FAILED', 'Failed'

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='exam_attempts'
    )
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='attempts'
    )
    start_time = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    
    total_questions = models.IntegerField(default=0)
    attempted_questions = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    wrong_answers = models.IntegerField(default=0)

    total_marks = models.FloatField(default=0.0)
    obtained_marks = models.FloatField(default=0.0)
    percentage = models.FloatField(default=0.0)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.IN_PROGRESS
    )
    is_completed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.student.username} - {self.exam.title} ({self.get_status_display()})"

    @property
    def end_time(self):
        """Calculates expected end time based on exam duration."""
        return self.start_time + timedelta(minutes=self.exam.duration_minutes)

    @property
    def remaining_seconds(self):
        """Calculates remaining seconds for the attempt."""
        now = timezone.now()
        end = self.end_time
        if now >= end or self.is_completed:
            return 0
        return int((end - now).total_seconds())

    @property
    def is_time_expired(self):
        """Checks if timer has reached zero."""
        return self.remaining_seconds <= 0


class StudentAnswer(models.Model):
    """
    Stores individual question answers chosen by a student during an attempt.
    """
    attempt = models.ForeignKey(
        ExamAttempt,
        on_delete=models.CASCADE,
        related_name='student_answers'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='student_answers'
    )
    selected_option = models.ForeignKey(
        Option,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='student_answers'
    )
    is_correct = models.BooleanField(default=False)
    marks_obtained = models.FloatField(default=0.0)

    def __str__(self):
        status = "Correct" if self.is_correct else "Incorrect"
        return f"Attempt #{self.attempt.id} - Q{self.question.id}: {status}"


class Result(models.Model):
    """
    Summary result record generated upon exam completion.
    """
    attempt = models.OneToOneField(
        ExamAttempt,
        on_delete=models.CASCADE,
        related_name='result'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Result: {self.attempt.student.username} - {self.attempt.exam.title} ({self.attempt.obtained_marks}/{self.attempt.total_marks})"
