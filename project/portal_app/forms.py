from django import forms
from .models import Student

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['student_id', 'student_name', 'department', 'specialization', 'mentor_name', 'mentor_id', 'mentor_email', 'mentor_phone']
        widgets = {
            'student_id': forms.TextInput(attrs={'class': 'form-control'}),
            'student_name': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Department'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Specialization'}),
            'mentor_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Mentor Name'}),
            'mentor_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Mentor ID'}),
            'mentor_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter Mentor Email'}),
            'mentor_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Mentor Phone'}),
        }

class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.xlsx'}))
