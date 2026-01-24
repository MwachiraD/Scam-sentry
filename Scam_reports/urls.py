from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView


urlpatterns=[
    path('', views.report_scam, name ='report_scam'),
    path('reports/', views.report_list, name='report_list'),
    path('thank-you/', views.thank_you, name='thank_you'),
    path('reports/resolve/<int:report_id>/', views.mark_resolved, name='mark_resolved'),
    path('login/', auth_views.LoginView.as_view(template_name='account/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('accounts/popup-close/', TemplateView.as_view(template_name='popup_close.html'), name='popup-close'),
    path('edit/<int:pk>/', views.edit_report, name='edit_report'),
    path('create-scam-types/', views.create_scam_types, name='create_scam_types'),

]
