from django.contrib import admin
from .models import Exam, Question, Option


class OptionInline(admin.TabularInline):
    model = Option
    extra = 4
    max_num = 4


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'duration_minutes', 'total_marks', 'pass_marks', 'question_count', 'is_published', 'created_at')
    list_filter = ('is_published', 'created_at', 'created_by')
    search_fields = ('title', 'description', 'created_by__username')
    inlines = [QuestionInline]
    ordering = ('-created_at',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'exam', 'marks', 'order', 'created_at')
    list_filter = ('exam', 'marks')
    search_fields = ('question_text', 'exam__title')
    inlines = [OptionInline]


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('option_text', 'question', 'is_correct')
    list_filter = ('is_correct', 'question__exam')
    search_fields = ('option_text', 'question__question_text')
