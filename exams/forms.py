from django import forms
from django.core.exceptions import ValidationError
from .models import Exam, Question, Option


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['title', 'description', 'duration_minutes', 'total_marks', 'pass_marks', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Computer Networks Midterm'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter exam instructions or syllabus details...'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'total_marks': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'pass_marks': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        total_marks = cleaned_data.get('total_marks')
        pass_marks = cleaned_data.get('pass_marks')

        if total_marks and pass_marks and pass_marks > total_marks:
            self.add_error('pass_marks', "Passing marks cannot be greater than Total marks.")
        return cleaned_data


class QuestionWithOptionsForm(forms.Form):
    """
    Beginner-friendly form to add or edit an MCQ question along with 4 choices.
    """
    question_text = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter question statement...'}),
        label="Question Statement"
    )
    marks = forms.IntegerField(
        initial=1,
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label="Marks"
    )
    order = forms.IntegerField(
        initial=1,
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label="Sequence Order"
    )

    option_1 = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option A'}),
        label="Option A"
    )
    option_2 = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option B'}),
        label="Option B"
    )
    option_3 = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option C'}),
        label="Option C"
    )
    option_4 = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option D'}),
        label="Option D"
    )

    CORRECT_CHOICES = [
        ('1', 'Option A'),
        ('2', 'Option B'),
        ('3', 'Option C'),
        ('4', 'Option D'),
    ]
    correct_option = forms.ChoiceField(
        choices=CORRECT_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label="Select Correct Option"
    )
