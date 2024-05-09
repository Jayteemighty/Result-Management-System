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

    def get_queryset(self):
        queryset = super().get_queryset()
        for result in queryset:
            self.calculate_cgpa(result)
        return queryset

    def calculate_cgpa(self, result):
        cwgp = 0  # Cumulative Weighted points
        cu = 0    # Cumulative Units

        for key, value in result.marks.items():
            if key.endswith('_mark'):
                subject_id = key.split('_')[1]
                unit_key = f'subject_{subject_id}_unit'
                point_key = f'subject_{subject_id}_point'

                if unit_key in result.unit and point_key in result.point:
                    unit = float(result.unit[unit_key])
                    point = float(result.point[point_key])
                    wgp = round(unit * point, 2)
                    cwgp += wgp
                    cu += unit

        if cu > 0:
            result.cgpa = round(cwgp / cu, 2)
        else:
            result.cgpa = 0
        result.save()  # Update the result with the calculated CGPA


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['main_page_title'] = 'Manage Results'
        context['panel_name'] = 'Results'
        context['panel_title'] = 'View Results Info'
        context['subjects'] = Subject.objects.all()  # Pass all subjects to the template
        context['i'] = range(len(context['subjects']))  # Generate a range of integers based on the number of subjects
        context['marks'] = [f'subject_{index}_mark' for index in context['i']]  # Generate the marks list dynamically
        return context