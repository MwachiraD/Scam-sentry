from django.urls import path, include
from . import views
from .views import report_scam , thank_you ,mark_resolved, user_dashboard
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from django.http import HttpResponse

urlpatterns=[
    path('', views.report_scam, name ='report_scam'),
    path('reports/', views.report_list, name='report_list'),
    path('thank-you/', views.thank_you, name='thank_you'),
    path('reports/resolve/<int:report_id>/', mark_resolved, name='mark_resolved'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('dashboard/', user_dashboard, name='user_dashboard'),
    path('accounts/popup-close/', TemplateView.as_view(template_name='account/popup-close.html'), name='popup-close'),
    path('create-types/', create_scam_types),
    path('edit/<int:pk>/', views.edit_report, name='edit_report'),

]