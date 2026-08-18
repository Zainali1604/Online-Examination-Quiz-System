from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import teacher_required
from .models import Exam, Question, Option
from .forms import ExamForm, QuestionWithOptionsForm


@login_required
def exam_list(request):
    """
    Lists exams according to user role:
    - Teacher sees exams they created (both drafts and published).
    - Student sees all published exams.
    """
    if request.user.is_teacher:
        exams = Exam.objects.filter(created_by=request.user)
    else:
        exams = Exam.objects.filter(is_published=True)

    context = {
        'exams': exams,
    }
    return render(request, 'exams/exam_list.html', context)


@login_required
def exam_detail(request, exam_id):
    """
    Displays details and instructions for a specific exam.
    """
    exam = get_object_or_404(Exam, id=exam_id)

    # Security check: Students cannot view unpublished draft exams
    if request.user.is_student and not exam.is_published:
        messages.error(request, "This exam is not available.")
        return redirect('exams:exam_list')

    context = {
        'exam': exam,
        'questions': exam.questions.all(),
    }
    return render(request, 'exams/exam_detail.html', context)


@teacher_required
def create_exam(request):
    """
    Allows a Teacher to create a new Examination.
    """
    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.created_by = request.user
            exam.save()
            messages.success(request, f"Exam '{exam.title}' created successfully! Now add questions.")
            return redirect('exams:question_list', exam_id=exam.id)
    else:
        form = ExamForm()

    return render(request, 'exams/create_exam.html', {'form': form})


@teacher_required
def edit_exam(request, exam_id):
    """
    Allows a Teacher to edit an existing Examination.
    """
    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    if request.method == 'POST':
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            form.save()
            messages.success(request, "Exam updated successfully.")
            return redirect('exams:exam_detail', exam_id=exam.id)
    else:
        form = ExamForm(instance=exam)

    return render(request, 'exams/edit_exam.html', {'form': form, 'exam': exam})


@teacher_required
def delete_exam(request, exam_id):
    """
    Allows a Teacher to delete an Examination.
    """
    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    if request.method == 'POST':
        title = exam.title
        exam.delete()
        messages.success(request, f"Exam '{title}' has been deleted.")
        return redirect('exams:exam_list')

    return render(request, 'exams/confirm_delete.html', {'object': exam, 'type': 'Exam'})


@teacher_required
def toggle_publish_exam(request, exam_id):
    """
    Publishes or unpublishes an exam.
    """
    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    if exam.question_count == 0 and not exam.is_published:
        messages.error(request, "Cannot publish an exam with 0 questions. Add questions first.")
        return redirect('exams:question_list', exam_id=exam.id)

    exam.is_published = not exam.is_published
    exam.save()
    status = "published" if exam.is_published else "unpublished"
    messages.success(request, f"Exam '{exam.title}' is now {status}.")
    return redirect('exams:exam_detail', exam_id=exam.id)


@teacher_required
def question_list(request, exam_id):
    """
    Displays all questions added under an exam.
    """
    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    questions = exam.questions.all()
    context = {
        'exam': exam,
        'questions': questions,
    }
    return render(request, 'exams/question_list.html', context)


@teacher_required
def add_question(request, exam_id):
    """
    Allows Teacher to add an MCQ question with 4 options.
    """
    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    next_order = exam.question_count + 1

    if request.method == 'POST':
        form = QuestionWithOptionsForm(request.POST)
        if form.is_valid():
            # 1. Create Question
            question = Question.objects.create(
                exam=exam,
                question_text=form.cleaned_data['question_text'],
                marks=form.cleaned_data['marks'],
                order=form.cleaned_data['order'],
            )

            # 2. Create 4 Options
            correct_idx = form.cleaned_data['correct_option']
            options_text = [
                form.cleaned_data['option_1'],
                form.cleaned_data['option_2'],
                form.cleaned_data['option_3'],
                form.cleaned_data['option_4'],
            ]

            for idx, text in enumerate(options_text, start=1):
                Option.objects.create(
                    question=question,
                    option_text=text,
                    is_correct=(str(idx) == correct_idx)
                )

            messages.success(request, "Question and options added successfully!")
            if 'add_another' in request.POST:
                return redirect('exams:add_question', exam_id=exam.id)
            return redirect('exams:question_list', exam_id=exam.id)
    else:
        form = QuestionWithOptionsForm(initial={'order': next_order})

    return render(request, 'exams/add_question.html', {'form': form, 'exam': exam})


@teacher_required
def edit_question(request, question_id):
    """
    Allows Teacher to edit an existing question and its 4 options.
    """
    question = get_object_or_404(Question, id=question_id, exam__created_by=request.user)
    options = list(question.options.all())

    initial_data = {
        'question_text': question.question_text,
        'marks': question.marks,
        'order': question.order,
    }

    correct_option_val = '1'
    for idx, opt in enumerate(options, start=1):
        initial_data[f'option_{idx}'] = opt.option_text
        if opt.is_correct:
            correct_option_val = str(idx)

    initial_data['correct_option'] = correct_option_val

    if request.method == 'POST':
        form = QuestionWithOptionsForm(request.POST)
        if form.is_valid():
            question.question_text = form.cleaned_data['question_text']
            question.marks = form.cleaned_data['marks']
            question.order = form.cleaned_data['order']
            question.save()

            correct_idx = form.cleaned_data['correct_option']
            new_options_text = [
                form.cleaned_data['option_1'],
                form.cleaned_data['option_2'],
                form.cleaned_data['option_3'],
                form.cleaned_data['option_4'],
            ]

            question.options.all().delete()
            for idx, text in enumerate(new_options_text, start=1):
                Option.objects.create(
                    question=question,
                    option_text=text,
                    is_correct=(str(idx) == correct_idx)
                )

            messages.success(request, "Question updated successfully!")
            return redirect('exams:question_list', exam_id=question.exam.id)
    else:
        form = QuestionWithOptionsForm(initial=initial_data)

    return render(request, 'exams/add_question.html', {'form': form, 'exam': question.exam, 'is_edit': True})


@teacher_required
def delete_question(request, question_id):
    """
    Deletes a question.
    """
    question = get_object_or_404(Question, id=question_id, exam__created_by=request.user)
    exam_id = question.exam.id
    if request.method == 'POST':
        question.delete()
        messages.success(request, "Question deleted.")
        return redirect('exams:question_list', exam_id=exam_id)

    return render(request, 'exams/confirm_delete.html', {'object': question, 'type': 'Question'})
