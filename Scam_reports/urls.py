from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView


urlpatterns=[
    path('', views.report_scam, name ='report_scam'),
    path('reports/', views.report_list, name='report_list'),
    path('reports/<int:report_id>/', views.report_detail, name='report_detail'),
    path('reports/<int:report_id>/follow/', views.follow_report, name='follow_report'),
    path('reports/follow/confirm/<str:token>/', views.verify_report_follow, name='verify_report_follow'),
    path('reports/<int:report_id>/comment/', views.add_comment, name='add_comment'),
    path('reports/<int:report_id>/watch/', views.add_watchlist, name='add_watchlist'),
    path('thank-you/', views.thank_you, name='thank_you'),
    path('reports/resolve/<int:report_id>/', views.mark_resolved, name='mark_resolved'),
    path('reports/<int:report_id>/encounter/', views.encounter_report, name='report_encounter'),
    path('reports/<int:report_id>/report-abuse/', views.report_abuse, name='report_abuse'),
    path('login/', auth_views.LoginView.as_view(template_name='account/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('watchlist/', views.watchlist, name='watchlist'),
    path('moderation-queue/', views.moderation_queue, name='moderation_queue'),
    path('moderation-queue/<int:report_id>/approve/', views.approve_report, name='approve_report'),
    path('moderation-queue/<int:report_id>/reject/', views.reject_report, name='reject_report'),
    path('api/init/', views.deploy_init, name='deploy_init'),
    path('api/cron/weekly-digest/', views.cron_weekly_digest, name='cron_weekly_digest'),
    path('digest/subscribe/', views.digest_subscribe, name='digest_subscribe'),
    path('digest/confirm/<str:token>/', views.verify_digest_subscription, name='verify_digest_subscription'),
    path('policy/', views.policy, name='policy'),
    path('accounts/popup-close/', TemplateView.as_view(template_name='popup_close.html'), name='popup-close'),
    path('edit/<int:pk>/', views.edit_report, name='edit_report'),
    path('create-scam-types/', views.create_scam_types, name='create_scam_types'),

]
