from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    CreateView, ListView, UpdateView, DeleteView
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from results.models import DeclareResult
from results.forms import DeclareResultForm
from subjects.models import SubjectCombination, Subject
from student_classes.models import StudentClass
from students.models import Student
from django.http import HttpResponse, JsonResponse

from django.core import serializers
import json

# Create your views here.

def validate_data(request):
    smt = SubjectCombination.objects.all()
    data = {}
    if request.method == "GET":
        rc = request.GET['selectedClass']
        subjects = []
        for s in smt:
            if s.select_class.class_name in rc and s.select_class.department in rc:
                subjects.append(s.select_subject)
        sir_subjects = serializers.serialize('json', subjects)
        data['subjects'] = sir_subjects
        return JsonResponse(data)
    subjects = None
    data['result'] = 'you made a request with empty data'
    return HttpResponse(json.dumps(data), content_type="application/json")

def declare_result_view(request):
    context = {}
    if request.method == "POST":
        form = DeclareResultForm(request.POST)
        if form.is_valid():
            select_class = form.cleaned_data['select_class']
            select_student = form.cleaned_data['select_student']
            marks = {}
            point = {}
            unit = {}
            for key, value in request.POST.items():
                if key.startswith('subject_'):
                    if key.endswith('_mark'):
                        marks[key] = value
                    elif key.endswith('_point'):
                        point[key] = value
                    elif key.endswith('_unit'):
                        unit[key] = value
            DeclareResult.objects.create(
                select_class=select_class,
                select_student=select_student,
                marks=marks,
                point=point,
                unit=unit
            )
            return redirect('results:result_list')
    else:
        form = DeclareResultForm()
        context['main_page_title'] = 'Declare Students Result'
        context['panel_name'] = 'Results'
        context['panel_title'] = 'Declare Result'
        context['form'] = form
    return render(request, "results/declareresult_form.html", context)



def setup_update_view(request):
    data = {}
    if request.method == "GET":
        pk_value = int(request.GET['pk_value'])
        result_obj = get_object_or_404(DeclareResult, pk = pk_value)
        dt = result_obj.marks
        data['dt'] = dt
        return HttpResponse(json.dumps(data), content_type="application/json")
    return HttpResponse(json.dumps(data), content_type="application/json")

@login_required
def result_update_view(request, pk):
    result = get_object_or_404(DeclareResult, pk=pk)
    form = DeclareResultForm(instance=result)
    context = {}
    context['main_page_title'] = 'Update Students Result'
    context['panel_name'] = 'Results'
    context['panel_title'] = 'Update Result'
    context['form'] = form
    context['pk'] = pk
    if request.method == "POST":
        all_data = request.POST
        data = json.loads(json.dumps(all_data))
        data.pop('csrfmiddlewaretoken')
        pk = data['select_class']
        clas = StudentClass.objects.get(id=pk)
        pk = data['select_student']
        student = Student.objects.get(id=pk)
        data.pop('select_class')
        data.pop('select_student')
        print('Modified Data = ', data)
        result.select_class = clas
        result.select_student = student
        result.marks = data
        result.unit= data
        result.point = data
        result.save()
        print('\nResult updated\n')
        return redirect('results:result_list')
    return render(request, "results/update_form.html", context)

@login_required
def result_delete_view(request, pk):
    obj = get_object_or_404(DeclareResult, pk=pk)
    if request.method == "POST":
        obj.delete()
        return redirect('results:result_list')
    return render(request, "results/result_delete.html", {"object":obj})


class DeclareResultListView(ListView):
    model = DeclareResult
    template_name = 'results/declareresult_list.html'
    
    def result(request, pk):
        object = get_object_or_404(DeclareResult, pk=pk)

        subjects = []
        wgp = []
        cwgp = 0  
        cu = 0    
    
        for key, value in object.marks.items():
                unit = float(object.unit)
                point = float(object.point)
                wgp = round(unit * point, 2)  # Calculate WGP
                cwgp += wgp  # Update CWGP
                cu += unit   # Update CU
        if cu != 0:
            cgpa = round(cwgp / cu, 2)
        else:
            cgpa = 0

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['main_page_title'] = 'Manage Results'
        context['panel_name'] = 'Results'
        context['panel_title'] = 'View Results Info'
        context['subjects'] = Subject.objects.all()  # Pass all subjects to the template
        context['i'] = range(len(context['subjects']))  # Generate a range of integers based on the number of subjects
        context['marks'] = [f'subject_{index}_mark' for index in context['i']]  # Generate the marks list dynamically
        return context