from django.db import models
from django.conf import settings


class Exam(models.Model):
    """
    Represents an examination created by a Teacher.
    """
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_exams',
        help_text="Teacher who created this exam"
    )
    title = models.CharField(max_length=200, help_text="Exam Title (e.g. Data Structures Midterm)")
    description = models.TextField(blank=True, help_text="Instructions or exam description")
    duration_minutes = models.PositiveIntegerField(
        default=30,
        help_text="Exam duration in minutes"
    )
    total_marks = models.PositiveIntegerField(
        default=100,
        help_text="Total marks for the exam"
    )
    pass_marks = models.PositiveIntegerField(
        default=40,
        help_text="Passing marks required"
    )
    is_published = models.BooleanField(
        default=False,
        help_text="If published, students can view and attempt this exam"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        status = "Published" if self.is_published else "Draft"
        return f"{self.title} ({status})"

    @property
    def question_count(self):
        """Returns the total number of questions added to this exam."""
        return self.questions.count()

    @property
    def total_question_marks(self):
        """Sum of marks of all added questions."""
        return sum(q.marks for q in self.questions.all())


class Question(models.Model):
    """
    Multiple Choice Question belonging to an Exam.
    """
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    question_text = models.TextField(help_text="Question statement")
    marks = models.PositiveIntegerField(default=1, help_text="Marks for this question")
    order = models.PositiveIntegerField(default=1, help_text="Question sequence order")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}..."

    @property
    def correct_option(self):
        """Returns the option marked as correct."""
        return self.options.filter(is_correct=True).first()


class Option(models.Model):
    """
    Option choice for an MCQ Question.
    Each Question typically has 4 Options, with 1 marked as correct.
    """
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='options'
    )
    option_text = models.CharField(max_length=500, help_text="Option answer text")
    is_correct = models.BooleanField(
        default=False,
        help_text="Mark True if this is the correct answer"
    )

    def __str__(self):
        correct = " [CORRECT]" if self.is_correct else ""
        return f"{self.option_text}{correct}"
