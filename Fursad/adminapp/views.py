from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q

def admin_login(request):
    if request.method == 'POST':
        identifier = request.POST.get('identifier')
        password = request.POST.get('password')
        
        # Check if user exists by username or email
        user = authenticate(request, username=identifier, password=password)
        
        if user is None:
            # If standard authenticate fails, try to find user by email
            try:
                user_obj = User.objects.get(Q(username=identifier) | Q(email=identifier))
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

        if user is not None:
            if user.is_superuser or user.is_staff:
                login(request, user)
                return redirect('adminapp:dashboard')
            else:
                messages.error(request, "Access Denied: You are not an admin.")
        else:
            messages.error(request, "Invalid username/email or password.")
            
    return redirect(request.META.get('HTTP_REFERER', 'home'))

from companyapp.models import Company_DB
from shaqodonapp.models import shaqod_DB
from jobsapp.models import jops_DB

def admin_dashboard(request):
    if not (request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff)):
        return redirect('home')
        
    total_companies = Company_DB.objects.count()
    total_jobseekers = shaqod_DB.objects.count()
    open_jobs = jops_DB.objects.filter(j_active=True).count()
    pending_companies = Company_DB.objects.filter(c_active=False)
    pending_verifications = pending_companies.count()
    
    # Get up to 5 recently registered companies needing verification
    recent_verifications = pending_companies.order_by('-c_joined')[:5]

    context = {
        'total_companies': total_companies,
        'total_jobseekers': total_jobseekers,
        'open_jobs': open_jobs,
        'pending_verifications': pending_verifications,
        'recent_verifications': recent_verifications,
    }
    
    return render(request, 'adminapp/dashboard.html', context)

from django.shortcuts import get_object_or_404

def admin_companies(request):
    if not (request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff)):
        return redirect('home')
        
    # Order by c_active ASC (False first, meaning pending verifications are at the top), then by joined date DESC
    companies = Company_DB.objects.all().order_by('c_active', '-c_joined')
    pending_verifications = Company_DB.objects.filter(c_active=False).count()
    
    context = {
        'companies': companies,
        'pending_verifications': pending_verifications,
    }
    return render(request, 'adminapp/companies.html', context)

def admin_company_activate(request, company_id):
    if not (request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff)):
        return redirect('home')
    company = get_object_or_404(Company_DB, id=company_id)
    company.c_active = True
    company.save()
    messages.success(request, f"Company {company.c_name} has been activated successfully.")
    return redirect('adminapp:companies')

def admin_company_deactivate(request, company_id):
    if not (request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff)):
        return redirect('home')
    company = get_object_or_404(Company_DB, id=company_id)
    company.c_active = False
    company.save()
    messages.warning(request, f"Company {company.c_name} has been deactivated.")
    return redirect('adminapp:companies')

def admin_company_delete(request, company_id):
    if not (request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff)):
        return redirect('home')
    company = get_object_or_404(Company_DB, id=company_id)
    company_name = company.c_name
    company.delete()
    messages.success(request, f"Company {company_name} has been deleted.")
    return redirect('adminapp:companies')

from applications.models import Application_DB

def admin_company_detail(request, company_id):
    if not (request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff)):
        return redirect('home')
        
    company = get_object_or_404(Company_DB, id=company_id)
    jobs = jops_DB.objects.filter(j_company=company).order_by('-j_posted')
    applications = Application_DB.objects.filter(a_job__j_company=company).order_by('-a_applied_date')
    
    context = {
        'company': company,
        'jobs': jobs,
        'applications': applications,
        'total_jobs': jobs.count(),
        'total_applications': applications.count(),
    }
    return render(request, 'adminapp/company_detail.html', context)


from shaqodonapp.models import shaqod_DB

def admin_jobseekers(request):
    if not (request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff)):
        return redirect('home')
        
    jobseekers = shaqod_DB.objects.all().order_by('-s_created')
    total_jobseekers = jobseekers.count()
    active_jobseekers = jobseekers.filter(s_status=True).count()
    
    context = {
        'jobseekers': jobseekers,
        'total_jobseekers': total_jobseekers,
        'active_jobseekers': active_jobseekers,
    }
    return render(request, 'adminapp/jobseekers.html', context)

def admin_jobseeker_toggle(request, jobseeker_id):
    if not (request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff)):
        return redirect('home')
    
    jobseeker = get_object_or_404(shaqod_DB, id=jobseeker_id)
    jobseeker.s_status = not jobseeker.s_status
    jobseeker.save()
    
    status_text = "activated" if jobseeker.s_status else "deactivated"
    messages.success(request, f"Jobseeker {jobseeker.s_fullname} has been {status_text}.")
    return redirect('adminapp:jobseekers')

def admin_jobseeker_delete(request, jobseeker_id):
    if not (request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff)):
        return redirect('home')
        
    jobseeker = get_object_or_404(shaqod_DB, id=jobseeker_id)
    name = jobseeker.s_fullname
    jobseeker.delete()
    messages.success(request, f"Jobseeker {name} has been permanently deleted.")
    return redirect('adminapp:jobseekers')

def admin_jobseeker_detail(request, jobseeker_id):
    if not (request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff)):
        return redirect('home')
        
    jobseeker = get_object_or_404(shaqod_DB, id=jobseeker_id)
    applications = Application_DB.objects.filter(a_shaqod=jobseeker).order_by('-a_applied_date')
    
    context = {
        'jobseeker': jobseeker,
        'applications': applications,
        'total_applications': applications.count(),
        'accepted_applications': applications.filter(a_status='accepted').count(),
        'rejected_applications': applications.filter(a_status='rejected').count(),
    }
    return render(request, 'adminapp/jobseeker_detail.html', context)

def admin_job_delete(request, job_id):
    if not (request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff)):
        return redirect('home')
        
    job = get_object_or_404(jops_DB, id=job_id)
    company_id = job.j_company.id
    job_title = job.j_title
    job.delete()
    
    messages.success(request, f"Job '{job_title}' has been deleted successfully.")
    
    # Check if referer contains company detail, if so return there
    referer = request.META.get('HTTP_REFERER')
    if referer and f'/adminapp/companies/{company_id}/' in referer:
        return redirect('adminapp:company_detail', company_id=company_id)
    
    # Default fallback
    return redirect('adminapp:jobs')

from django.utils import timezone

def admin_jobs(request):
    if not (request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff)):
        return redirect('home')
        
    jobs = jops_DB.objects.all().order_by('-j_posted')
    total_jobs = jobs.count()
    active_jobs = jobs.filter(j_active=True).count()
    
    # For filtering
    companies = Company_DB.objects.filter(c_active=True).order_by('c_name')
    locations = jops_DB.objects.exclude(j_location__isnull=True).exclude(j_location__exact='').values_list('j_location', flat=True).distinct()
    jobtypes = jops_DB.jobtype
    
    today = timezone.now().date()
    
    context = {
        'jobs': jobs,
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'companies': companies,
        'locations': locations,
        'jobtypes': jobtypes,
        'today': today,
    }
    return render(request, 'adminapp/jobs.html', context)

import json
from django.db.models import Count

def admin_analyze(request):
    if not (request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff)):
        return redirect('home')

    # Quick Stats
    total_companies = Company_DB.objects.count()
    total_jobseekers = shaqod_DB.objects.count()
    total_jobs = jops_DB.objects.count()
    total_applications = Application_DB.objects.count()

    # Application Status Data
    apps_pending = Application_DB.objects.filter(a_status='pending').count()
    apps_accepted = Application_DB.objects.filter(a_status='accepted').count()
    apps_rejected = Application_DB.objects.filter(a_status='rejected').count()

    # Job Types Data
    job_types = list(jops_DB.objects.values('j_jobtype').annotate(count=Count('id')).order_by('j_jobtype'))
    # Clean up labels (e.g. replacing underscore with space, title case)
    jtype_labels = [str(item['j_jobtype']).replace('_', ' ').title() if item['j_jobtype'] else 'Unknown' for item in job_types]
    jtype_counts = [item['count'] for item in job_types]

    context = {
        'total_companies': total_companies,
        'total_jobseekers': total_jobseekers,
        'total_jobs': total_jobs,
        'total_applications': total_applications,

        # Chart Data
        'app_status_data': json.dumps([apps_pending, apps_accepted, apps_rejected]),
        'jtype_labels': json.dumps(jtype_labels),
        'jtype_counts': json.dumps(jtype_counts),
        'user_distribution_data': json.dumps([total_companies, total_jobseekers]),
    }
    return render(request, 'adminapp/anylize.html', context)

from django.contrib.auth.models import User

def admin_profile(request):
    if not (request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff)):
        return redirect('home')
        
    if request.method == 'POST':
        user = request.user
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if username:
            user.username = username
        if email:
            user.email = email
        if password:
            user.set_password(password)
        user.save()
        messages.success(request, "Your profile has been updated successfully. Please login again if you changed password.")
        return redirect('adminapp:profile')

    admins = User.objects.filter(is_staff=True).order_by('id')
    
    context = {
        'admins': admins
    }
    return render(request, 'adminapp/profile.html', context)

def admin_add(request):
    if not (request.user.is_authenticated and request.user.is_superuser):
        messages.error(request, "Only Superusers can add new admins.")
        return redirect('adminapp:profile')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        is_super = request.POST.get('is_superuser') == 'on'
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.is_staff = True
            user.is_superuser = is_super
            user.save()
            messages.success(request, f"Admin {username} added successfully.")
            
    return redirect('adminapp:profile')

def admin_edit(request, admin_id):
    if not (request.user.is_authenticated and request.user.is_superuser):
        messages.error(request, "Only Superusers can edit admins.")
        return redirect('adminapp:profile')
        
    if request.method == 'POST':
        admin = get_object_or_404(User, id=admin_id)
        admin.username = request.POST.get('username')
        admin.email = request.POST.get('email')
        
        if request.POST.get('password'):
            admin.set_password(request.POST.get('password'))
            
        admin.is_superuser = request.POST.get('is_superuser') == 'on'
        admin.save()
        messages.success(request, f"Admin {admin.username} updated successfully.")
        
    return redirect('adminapp:profile')

def admin_delete(request, admin_id):
    if not (request.user.is_authenticated and request.user.is_superuser):
        messages.error(request, "Only Superusers can delete admins.")
        return redirect('adminapp:profile')
        
    admin = get_object_or_404(User, id=admin_id)
    if admin.id == request.user.id:
        messages.error(request, "You cannot delete yourself.")
    else:
        admin_name = admin.username
        admin.delete()
        messages.success(request, f"Admin {admin_name} has been removed.")
        
    return redirect('adminapp:profile')
