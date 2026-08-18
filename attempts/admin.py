from django.contrib import admin
from .models import ExamAttempt, StudentAnswer, Result


class StudentAnswerInline(admin.TabularInline):
    model = StudentAnswer
    extra = 0
    readonly_fields = ('question', 'selected_option', 'is_correct', 'marks_obtained')
    can_delete = False


@admin.register(ExamAttempt)
class ExamAttemptAdmin(admin.ModelAdmin):
    list_display = (
        'student', 'exam', 'obtained_marks', 'total_marks',
        'percentage', 'status', 'is_completed', 'start_time', 'submitted_at'
    )
    list_filter = ('status', 'is_completed', 'exam', 'start_time')
    search_fields = ('student__username', 'student__email', 'exam__title')
    inlines = [StudentAnswerInline]
    ordering = ('-start_time',)


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'selected_option', 'is_correct', 'marks_obtained')
    list_filter = ('is_correct', 'attempt__exam')
    search_fields = ('attempt__student__username', 'question__question_text')


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'created_at')
    search_fields = ('attempt__student__username', 'attempt__exam__title')
