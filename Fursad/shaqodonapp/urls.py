from django.urls import path
from . import views

app_name = 'shaqodonapp'

urlpatterns = [
    path('dashboard/', views.shaqodon_dashboard, name='shaqodon_dashboard'),
    path('login/', views.shaqodon_login, name='shaqodon_login'),
    path('register/', views.shaqodon_register, name='shaqodon_register'),
    path('logout/', views.shaqodon_logout, name='shaqodon_logout'),
    path('profile/', views.shaqodon_profile, name='shaqodon_profile'),
    path('applications/', views.shaqodon_applications, name='shaqodon_applications'),
    path('jobs/', views.shaqodon_jobs, name='shaqodon_jobs'),
    path('companies/', views.shaqodon_companies, name='shaqodon_companies'),
    path('company/<int:company_id>/', views.shaqodon_company_detail, name='shaqodon_company_detail'),
    path('jobs/<int:job_id>/', views.shaqodon_job_detail, name='shaqodon_job_detail'),
    path('edit-application/<int:app_id>/', views.edit_application, name='edit_application'),
    path('delete-application/<int:app_id>/', views.delete_application, name='delete_application'),
]
