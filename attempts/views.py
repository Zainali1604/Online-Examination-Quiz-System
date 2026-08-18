from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from accounts.decorators import student_required
from exams.models import Exam, Question, Option
from .models import ExamAttempt, StudentAnswer, Result


@student_required
def start_exam(request, exam_id):
    """
    Initializes a new exam attempt session for a student.
    """
    exam = get_object_or_404(Exam, id=exam_id, is_published=True)

    if exam.question_count == 0:
        messages.error(request, "This exam has no questions available yet.")
        return redirect('exams:exam_list')

    # Check if student already has an incomplete ongoing attempt for this exam
    ongoing_attempt = ExamAttempt.objects.filter(
        student=request.user,
        exam=exam,
        is_completed=False
    ).first()

    if ongoing_attempt:
        if ongoing_attempt.is_time_expired:
            # Auto finalize expired attempt
            return evaluate_and_finalize_attempt(request, ongoing_attempt)
        return redirect('attempts:attempt_exam', attempt_id=ongoing_attempt.id)

    # Create new attempt
    attempt = ExamAttempt.objects.create(
        student=request.user,
        exam=exam,
        total_questions=exam.question_count,
        total_marks=exam.total_marks
    )

    messages.info(request, f"Exam '{exam.title}' started! Timer set for {exam.duration_minutes} minutes.")
    return redirect('attempts:attempt_exam', attempt_id=attempt.id)


@student_required
def attempt_exam(request, attempt_id):
    """
    Renders active exam question paper and countdown timer.
    """
    attempt = get_object_or_404(ExamAttempt, id=attempt_id, student=request.user)

    if attempt.is_completed:
        return redirect('attempts:result', attempt_id=attempt.id)

    # Backend timing check
    if attempt.is_time_expired:
        messages.warning(request, "Exam time has expired! Submitting your test automatically.")
        return evaluate_and_finalize_attempt(request, attempt, post_data=request.POST if request.method == 'POST' else None)

    context = {
        'attempt': attempt,
        'exam': attempt.exam,
        'questions': attempt.exam.questions.prefetch_related('options').all(),
        'remaining_seconds': attempt.remaining_seconds,
    }
    return render(request, 'attempts/attempt_exam.html', context)


@student_required
def submit_exam(request, attempt_id):
    """
    Handles student exam POST submission and triggers evaluation.
    """
    attempt = get_object_or_404(ExamAttempt, id=attempt_id, student=request.user)

    if attempt.is_completed:
        return redirect('attempts:result', attempt_id=attempt.id)

    if request.method == 'POST':
        return evaluate_and_finalize_attempt(request, attempt, post_data=request.POST)

    return redirect('attempts:attempt_exam', attempt_id=attempt.id)


def evaluate_and_finalize_attempt(request, attempt, post_data=None):
    """
    Core Evaluation Engine:
    Compares selected options against correct answers, calculates score, percentage, and pass/fail.
    """
    if attempt.is_completed:
        return redirect('attempts:result', attempt_id=attempt.id)

    questions = attempt.exam.questions.prefetch_related('options').all()

    total_obtained_marks = 0.0
    attempted_count = 0
    correct_count = 0
    wrong_count = 0

    # Delete any existing draft answers for clean re-evaluation
    attempt.student_answers.all().delete()

    for question in questions:
        selected_option_id = None
        if post_data:
            selected_option_id = post_data.get(f'question_{question.id}')

        selected_option = None
        is_correct = False
        marks_awarded = 0.0

        if selected_option_id:
            try:
                selected_option = Option.objects.get(id=selected_option_id, question=question)
                attempted_count += 1
                if selected_option.is_correct:
                    is_correct = True
                    marks_awarded = float(question.marks)
                    correct_count += 1
                else:
                    wrong_count += 1
            except Option.DoesNotExist:
                pass
        else:
            wrong_count += 1

        total_obtained_marks += marks_awarded

        # Save student answer record
        StudentAnswer.objects.create(
            attempt=attempt,
            question=question,
            selected_option=selected_option,
            is_correct=is_correct,
            marks_obtained=marks_awarded
        )

    # Compute final metrics
    attempt.submitted_at = timezone.now()
    attempt.total_questions = questions.count()
    attempt.attempted_questions = attempted_count
    attempt.correct_answers = correct_count
    attempt.wrong_answers = wrong_count
    attempt.obtained_marks = round(total_obtained_marks, 2)

    total_possible = float(attempt.exam.total_marks or 100)
    attempt.total_marks = total_possible
    
    if total_possible > 0:
        attempt.percentage = round((attempt.obtained_marks / total_possible) * 100, 2)
    else:
        attempt.percentage = 0.0

    if attempt.obtained_marks >= float(attempt.exam.pass_marks):
        attempt.status = ExamAttempt.Status.PASSED
    else:
        attempt.status = ExamAttempt.Status.FAILED

    attempt.is_completed = True
    attempt.save()

    # Save Result record
    Result.objects.get_or_create(attempt=attempt)

    if request:
        messages.success(request, "Exam submitted and evaluated successfully!")
    return redirect('attempts:result', attempt_id=attempt.id)


@login_required
def result_view(request, attempt_id):
    """
    Renders evaluation score report.
    """
    attempt = get_object_or_404(ExamAttempt, id=attempt_id)

    # Authorization security: Student can only view their own result, Teacher/Admin can view any
    if request.user.is_student and attempt.student != request.user:
        messages.error(request, "Access denied. You can only view your own results.")
        return redirect('dashboard:student_dashboard')

    context = {
        'attempt': attempt,
        'exam': attempt.exam,
    }
    return render(request, 'attempts/result.html', context)


@student_required
def attempt_history(request):
    """
    Lists all completed exam attempts for the logged-in student.
    """
    attempts = ExamAttempt.objects.filter(student=request.user, is_completed=True)
    return render(request, 'attempts/attempt_history.html', {'attempts': attempts})


@login_required
def answer_review(request, attempt_id):
    """
    Detailed review showing questions, selected options, correct answers, and marks obtained.
    """
    attempt = get_object_or_404(ExamAttempt, id=attempt_id)

    if request.user.is_student and attempt.student != request.user:
        messages.error(request, "Access denied.")
        return redirect('dashboard:student_dashboard')

    student_answers = attempt.student_answers.select_related('question', 'selected_option').all()

    context = {
        'attempt': attempt,
        'student_answers': student_answers,
    }
    return render(request, 'attempts/answer_review.html', context)
