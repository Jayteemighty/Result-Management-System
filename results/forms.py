from django.forms import ModelForm
from django import forms
from .models import DeclareResult

class DeclareResultForm(ModelForm):
    class Meta:
        model = DeclareResult
        fields = ['select_class', 'select_student'] #remember to add cgpa to fields
        widgets = {
            'select_class': forms.Select(attrs={'class': 'form-control'}),
            'select_student':  forms.Select(attrs={'class': 'form-control'}),
            #'cgpa': forms.NumberInput(attrs={'class': 'form-control'})
        }
        labels = {
            'select_class' : 'Class',
            'select_student' : 'Select Student',
            
            #'cgpa': 'CGPA' 
        }
