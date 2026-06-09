from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from companyapp.models import Company_DB
from jobsapp.models import jops_DB

# Create your views here.

def home(request):
    return render(request, 'coreapp/home.html')


def about(request):
    return render(request, 'coreapp/about.html')


def companies(request):
    query = request.GET.get('q', '')
    companies = Company_DB.objects.filter(c_active=True)
    if query:
        companies = companies.filter(Q(c_name__icontains=query) | Q(c_description__icontains=query))
    return render(request, 'coreapp/companies.html', {'companies': companies, 'query': query})


def jobs(request):
    query = request.GET.get('q', '')
    location = request.GET.get('location', '')
    job_type = request.GET.get('type', '')
    
    jobs_list = jops_DB.objects.filter(j_active=True, j_company__c_active=True)
    if query:
        jobs_list = jobs_list.filter(Q(j_title__icontains=query) | Q(j_description__icontains=query) | Q(j_company__c_name__icontains=query))
    if location:
        jobs_list = jobs_list.filter(j_location__icontains=location)
    if job_type:
        jobs_list = jobs_list.filter(j_jobtype=job_type)
        
    locations = jops_DB.objects.filter(j_active=True, j_company__c_active=True).values_list('j_location', flat=True).distinct()
    
    return render(request, 'coreapp/jobs.html', {
        'jobs': jobs_list.order_by('-j_posted'),
        'locations': locations,
        'query': query,
        'selected_location': location,
        'selected_type': job_type
    })


def contact(request):
    return render(request, 'coreapp/contact.html')


def privacy(request):
    return render(request, 'coreapp/privacy.html')


def terms(request):
    return render(request, 'coreapp/terms.html')


def services(request):
    return render(request, 'coreapp/services.html')


def company_login(request):
    if request.method == 'POST':
        identifier = request.POST.get('identifier')
        password = request.POST.get('password')
        
        company = Company_DB.objects.filter(c_email=identifier).first()
        if not company:
            company = Company_DB.objects.filter(c_username=identifier).first()
            
        if company and company.c_password == password:
            if company.c_active:
                request.session['company_id'] = company.id
                request.session['company_name'] = company.c_name
                if company.c_logo:
                    request.session['company_logo'] = company.c_logo.url
                return redirect('companyapp:company_dashboard')
            else:
                messages.warning(request, 'Only activated company can login')
                return redirect(request.META.get('HTTP_REFERER', 'home'))
        else:
            messages.error(request, 'Unavailable company')
            return redirect(request.META.get('HTTP_REFERER', 'home'))
            
    return redirect('home')


def company_register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if Company_DB.objects.filter(c_email=email).exists() or Company_DB.objects.filter(c_username=username).exists():
            messages.error(request, 'Email or Username already exists')
        else:
            Company_DB.objects.create(
                c_name=name,
                c_email=email,
                c_username=username,
                c_password=password,
                c_active=False
            )
            messages.success(request, 'Wait until admin activate you')
            
        return redirect(request.META.get('HTTP_REFERER', 'home'))
    else:
        return redirect('home')
