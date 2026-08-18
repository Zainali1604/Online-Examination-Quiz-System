from django.shortcuts import render
from django.db.models import Avg, Max, Min, Count
from accounts.decorators import student_required, teacher_required
from exams.models import Exam
from attempts.models import ExamAttempt, Result


@student_required
def student_dashboard(request):
    """
    Renders Student Dashboard with stats, recent exam results, and Chart.js analytics.
    """
    user = request.user
    available_exams = Exam.objects.filter(is_published=True)
    completed_attempts = ExamAttempt.objects.filter(student=user, is_completed=True)

    completed_count = completed_attempts.count()
    avg_percentage_query = completed_attempts.aggregate(Avg('percentage'))['percentage__avg']
    avg_percentage = round(avg_percentage_query, 2) if avg_percentage_query is not None else 0.0

    recent_results = completed_attempts.order_by('-submitted_at')[:5]

    # Chart.js Data preparation: Attempt history scores
    chart_labels = [att.exam.title[:15] + ('...' if len(att.exam.title) > 15 else '') for att in completed_attempts.order_by('submitted_at')]
    chart_scores = [att.percentage for att in completed_attempts.order_by('submitted_at')]

    context = {
        'available_count': available_exams.count(),
        'completed_count': completed_count,
        'avg_percentage': avg_percentage,
        'recent_results': recent_results,
        'chart_labels': chart_labels,
        'chart_scores': chart_scores,
    }
    return render(request, 'dashboard/student_dashboard.html', context)


@teacher_required
def teacher_dashboard(request):
    """
    Renders Teacher Dashboard with class stats, performance metrics, and Chart.js analytics.
    """
    user = request.user
    teacher_exams = Exam.objects.filter(created_by=user)
    
    total_exams = teacher_exams.count()
    published_exams = teacher_exams.filter(is_published=True).count()

    attempts = ExamAttempt.objects.filter(exam__in=teacher_exams, is_completed=True)
    total_attempts = attempts.count()
    total_students = attempts.values('student').distinct().count()

    avg_score_query = attempts.aggregate(Avg('percentage'))['percentage__avg']
    highest_score_query = attempts.aggregate(Max('percentage'))['percentage__max']
    lowest_score_query = attempts.aggregate(Min('percentage'))['percentage__min']

    class_avg_score = round(avg_score_query, 2) if avg_score_query is not None else 0.0
    highest_score = round(highest_score_query, 2) if highest_score_query is not None else 0.0
    lowest_score = round(lowest_score_query, 2) if lowest_score_query is not None else 0.0

    recent_attempts = attempts.order_by('-submitted_at')[:5]

    # Chart.js Exam Performance Breakdown
    exam_chart_labels = []
    exam_chart_avg_scores = []
    exam_chart_passed_count = []
    exam_chart_failed_count = []

    for exam in teacher_exams:
        exam_attempts = exam.attempts.filter(is_completed=True)
        if exam_attempts.exists():
            exam_chart_labels.append(exam.title[:15])
            exam_avg = exam_attempts.aggregate(Avg('percentage'))['percentage__avg'] or 0.0
            exam_chart_avg_scores.append(round(exam_avg, 2))
            exam_chart_passed_count.append(exam_attempts.filter(status=ExamAttempt.Status.PASSED).count())
            exam_chart_failed_count.append(exam_attempts.filter(status=ExamAttempt.Status.FAILED).count())

    context = {
        'total_exams': total_exams,
        'published_exams': published_exams,
        'total_students': total_students,
        'total_attempts': total_attempts,
        'class_avg_score': class_avg_score,
        'highest_score': highest_score,
        'lowest_score': lowest_score,
        'recent_attempts': recent_attempts,
        'exam_chart_labels': exam_chart_labels,
        'exam_chart_avg_scores': exam_chart_avg_scores,
        'exam_chart_passed_count': exam_chart_passed_count,
        'exam_chart_failed_count': exam_chart_failed_count,
    }
    return render(request, 'dashboard/teacher_dashboard.html', context)


@student_required
def performance_view(request):
    """
    Renders detailed performance breakdown with Chart.js for students.
    """
    user = request.user
    attempts = ExamAttempt.objects.filter(student=user, is_completed=True).order_by('submitted_at')

    passed_count = attempts.filter(status=ExamAttempt.Status.PASSED).count()
    failed_count = attempts.filter(status=ExamAttempt.Status.FAILED).count()

    labels = [att.exam.title for att in attempts]
    scores = [att.percentage for att in attempts]

    context = {
        'attempts': attempts,
        'passed_count': passed_count,
        'failed_count': failed_count,
        'labels': labels,
        'scores': scores,
    }
    return render(request, 'dashboard/performance.html', context)
