from django.urls import path
from . import views

app_name = 'companyapp'

urlpatterns = [
    path('dashboard/', views.company_dashboard, name='company_dashboard'),
    path('jobs/', views.company_jobs, name='company_jobs'),
    path('applications/', views.company_applications, name='company_applications'),
    path('jobs/post/', views.company_post_job, name='company_post_job'),
    path('profile/', views.company_profile, name='company_profile'),
    path('analyze/', views.company_analyze, name='company_analyze'),
    path('logout/', views.company_logout, name='company_logout'),
]
