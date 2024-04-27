from xhtml2pdf import pisa
from django.template.loader import get_template
from django.http import HttpResponse
from io import BytesIO
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import authenticate, login
from django.views.generic import TemplateView, View
from django.contrib.auth.models import User
from results.models import DeclareResult
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.core import serializers
from django.http import Http404
from django.http import Http404
import json

from student_classes.models import StudentClass
from results.models import DeclareResult
from subjects.models import Subject
from students.models import Student
from django.template.loader import render_to_string



def index(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard:dashboard')
        else:
            context = {'message':'Invalid User Name and Password'}
            return render(request, 'index.html', context)
    return render(request, 'index.html', {'name': 'Paul Emmanuel', })


class DashboardView(LoginRequiredMixin,TemplateView):
    template_name = "dashboard.html"

    
    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        context['cls'] = StudentClass.objects.count()
        context['results'] = DeclareResult.objects.count()
        context['students'] = Student.objects.count()
        context['subjects'] = Subject.objects.count()
        return context
    

def find_result_view(request):
    student_class = DeclareResult.objects.all()
    if request.method == "POST":
        data = request.POST
        # data = json.loads(form)
        matricno = int(data['matricid'])
        pk = int(data['class'])
        clss = get_object_or_404(DeclareResult, pk=pk)
        if clss.select_student.student_matricno == matricno:
            data = {
                'pk': data['class']
            }
            return JsonResponse(data)
        else:
            pk = '0'
            data = {
                'pk': pk
            }
            return JsonResponse(data)
    return render(request, 'find_result.html', {'class':student_class})

def result(request, pk):
    object = get_object_or_404(DeclareResult, pk=pk)
    
    # Initialize empty list to hold subject details
    subjects = []
    cwgp = 0  # Cumulative Weighted points
    cu = 0    # Cumulative Units
    
    # Iterate over the marks data
    for key, value in object.marks.items():
        # Check if the key represents a subject
        if key.endswith('_mark'):
            # Extract subject_id from the key
            subject_id = key.split('_')[1]
            
            # Attempt to retrieve the Subject instance
            try:
                subject = Subject.objects.get(pk=subject_id)
            except Subject.DoesNotExist:
                continue
            
            # Construct keys for unit and point using the same index
            unit_key = f'subject_{subject_id}_unit'
            point_key = f'subject_{subject_id}_point'
            
            # Check if both unit and point keys exist in the object
            if unit_key in object.unit and point_key in object.point:
                unit = float(object.unit[unit_key])
                point = float(object.point[point_key])
                wgp = round(unit * point, 2)  # Calculate WGP
                cwgp += wgp  # Update CWGP
                cu += unit   # Update CU
                
                subjects.append({
                    'name': subject.subject_name,
                    'mark': value,
                    'unit': unit,
                    'point': point,
                    'WGP': wgp,
                })
    
    # Calculate CGPA
    if cu != 0:
        cgpa = round(cwgp / cu, 2)
    else:
        cgpa = 0

    return render(request, 'result.html', {
        'object': object,
        'pk': pk,
        'subjects': subjects,
        'WGP': wgp,
        'CWGP': cwgp,
        'CU': cu,
        'CGPA': cgpa,
    })


class PasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    success_url = reverse_lazy('dashboard:dashboard')
    template_name = 'password_change_form.html'

    
    def get_context_data(self, **kwargs):
        context = super(PasswordChangeView, self).get_context_data(**kwargs)
        context['main_page_title'] = 'Admin Change Password'
        context['panel_title'] = 'Admin Change Password'
        return context