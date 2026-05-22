from django.urls import path
from.import views 

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('companies/', views.companies, name='companies'),
    path('jobs/', views.jobs, name='jobs'),
    path('contact/', views.contact, name='contact'),
    path('company-login/', views.company_login, name='company_login'),
    path('company-register/', views.company_register, name='company_register'),
    path('privacy-policy/', views.privacy, name='privacy'),
    path('terms-of-service/', views.terms, name='terms'),
    path('other-services/', views.services, name='services'),
]
