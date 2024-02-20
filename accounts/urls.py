from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
     path('sign-up/', views.sign_up, name='sign-up'),
    #path('login', views.LoginView.as_view(), name='login')
]