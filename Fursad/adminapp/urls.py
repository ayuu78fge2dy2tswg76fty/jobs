from django.urls import path
from . import views

app_name = 'adminapp'

urlpatterns = [
    path('', views.admin_dashboard, name='dashboard'),
    path('login/', views.admin_login, name='admin_login'),
    # Company Management
    path('companies/', views.admin_companies, name='companies'),
    path('companies/<int:company_id>/', views.admin_company_detail, name='company_detail'),
    path('companies/<int:company_id>/verify/', views.admin_company_verify, name='company_verify'),
    path('companies/<int:company_id>/unverify/', views.admin_company_unverify, name='company_unverify'),
    path('companies/<int:company_id>/activate/', views.admin_company_activate, name='company_activate'),
    path('companies/<int:company_id>/deactivate/', views.admin_company_deactivate, name='company_deactivate'),
    path('companies/<int:company_id>/delete/', views.admin_company_delete, name='company_delete'),
    path('companies/<int:company_id>/update_doc/', views.admin_company_update_doc, name='company_update_doc'),

    # Jobseeker Management
    path('jobseekers/', views.admin_jobseekers, name='jobseekers'),
    path('jobseekers/<int:jobseeker_id>/', views.admin_jobseeker_detail, name='jobseeker_detail'),
    path('jobseekers/<int:jobseeker_id>/toggle/', views.admin_jobseeker_toggle, name='jobseeker_toggle'),
    path('jobseekers/<int:jobseeker_id>/delete/', views.admin_jobseeker_delete, name='jobseeker_delete'),

    # Jobs Management
    path('jobs/', views.admin_jobs, name='jobs'),
    path('jobs/<int:job_id>/delete/', views.admin_job_delete, name='job_delete'),

    # Analytics
    path('analyze/', views.admin_analyze, name='analyze'),

    # Admin Profile & Management
    path('profile/', views.admin_profile, name='profile'),
    path('profile/add/', views.admin_add, name='admin_add'),
    path('profile/<int:admin_id>/edit/', views.admin_edit, name='admin_edit'),
    path('profile/<int:admin_id>/delete/', views.admin_delete, name='admin_delete'),
]
