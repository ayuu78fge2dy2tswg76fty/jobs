from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import date
from django.db.models import Count
from .models import Company_DB
from jobsapp.models import jops_DB
from applications.models import Application_DB

# Create your views here.

def company_dashboard(request):
    if 'company_id' not in request.session:
        return redirect('home')
        
    company_id = request.session['company_id']
    company = Company_DB.objects.filter(id=company_id).first()
    
    if not company or not company.c_active:
        if 'company_id' in request.session:
            del request.session['company_id']
        return redirect('home')
        
    # Automatically deactivate expired jobs
    jops_DB.objects.filter(j_company_id=company_id, j_active=True, j_EXP__lt=date.today()).update(j_active=False)
        
    company_jobs = jops_DB.objects.filter(j_company_id=company_id).annotate(app_count=Count('application_db')).order_by('-j_posted')
    total_jobs = company_jobs.count()
    active_jobs = company_jobs.filter(j_active=True).count()
    
    all_applications = Application_DB.objects.filter(a_job__j_company_id=company_id, a_deleted_by_company=False).order_by('-a_applied_date')
    total_apps = all_applications.count()
    shortlisted = all_applications.filter(a_status='accepted').count()
        
    context = {
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'total_applications': total_apps,
        'shortlisted': shortlisted,
        'recent_jobs': company_jobs[:5],
        'recent_applications': all_applications[:5],
    }
    return render(request, 'companyapp/dashboard.html', context)

def company_jobs(request):
    if 'company_id' not in request.session:
        return redirect('home')
        
    company_id = request.session['company_id']
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'post_job':
            try:
                company = Company_DB.objects.get(id=company_id)
                j_title = request.POST.get('j_title')
                j_jobtype = request.POST.get('j_jobtype')
                j_location = request.POST.get('j_location')
                j_salary = request.POST.get('j_salary') or None
                j_EXP = request.POST.get('j_EXP')
                j_description = request.POST.get('j_description')
                j_active = request.POST.get('j_active') == 'True'
                j_logo = request.FILES.get('j_logo')
                
                new_job = jops_DB(
                    j_company=company,
                    j_title=j_title,
                    j_jobtype=j_jobtype,
                    j_location=j_location,
                    j_salary=j_salary,
                    j_EXP=j_EXP,
                    j_description=j_description,
                    j_active=j_active,
                    j_logo=j_logo
                )
                new_job.save()
                messages.success(request, f"Job '{j_title}' has been successfully posted!")
                return redirect('companyapp:company_jobs')
            except Exception as e:
                messages.error(request, f"Error posting job: {e}")
                return redirect('companyapp:company_jobs')
                
        elif action == 'edit_job':
            try:
                job_id = request.POST.get('job_id')
                job = jops_DB.objects.get(id=job_id, j_company_id=company_id)
                
                job.j_title = request.POST.get('j_title')
                job.j_jobtype = request.POST.get('j_jobtype')
                job.j_location = request.POST.get('j_location')
                job.j_salary = request.POST.get('j_salary') or None
                job.j_EXP = request.POST.get('j_EXP')
                job.j_description = request.POST.get('j_description')
                job.j_active = request.POST.get('j_active') == 'True'
                
                if request.FILES.get('j_logo'):
                    job.j_logo = request.FILES.get('j_logo')
                    
                job.save()
                messages.success(request, f"Job '{job.j_title}' has been successfully updated!")
            except Exception as e:
                messages.error(request, f"Error updating job: {e}")
            return redirect('companyapp:company_jobs')
            
        elif action == 'delete_job':
            try:
                job_id = request.POST.get('job_id')
                job = jops_DB.objects.get(id=job_id, j_company_id=company_id)
                job_title = job.j_title
                job.delete()
                messages.success(request, f"Job '{job_title}' has been deleted.")
            except Exception as e:
                messages.error(request, f"Error deleting job: {e}")
            return redirect('companyapp:company_jobs')

    # Automatically deactivate expired jobs before fetching list
    jops_DB.objects.filter(j_company_id=company_id, j_active=True, j_EXP__lt=date.today()).update(j_active=False)

    company_jobs_list = jops_DB.objects.filter(j_company_id=company_id).order_by('-j_posted')
    
    context = {
        'jobs': company_jobs_list,
        'total_jobs': company_jobs_list.count(),
        'active_jobs': company_jobs_list.filter(j_active=True).count(),
        'closed_jobs': company_jobs_list.filter(j_active=False).count(),
    }
    return render(request, 'companyapp/jobs.html', context)

def company_post_job(request):
    if 'company_id' not in request.session:
        return redirect('home')
    return render(request, 'companyapp/dashboard.html') # Placeholder for post job template

def company_profile(request):
    if 'company_id' not in request.session:
        return redirect('home')
        
    company_id = request.session['company_id']
    company = Company_DB.objects.filter(id=company_id).first()
    
    if not company or not company.c_active:
        if 'company_id' in request.session:
            del request.session['company_id']
        return redirect('home')
        
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_profile':
            try:
                company.c_name = request.POST.get('c_name')
                company.c_email = request.POST.get('c_email')
                company.c_phone = request.POST.get('c_phone')
                company.c_description = request.POST.get('c_description')
                company.c_header_location = request.POST.get('c_header_location', '')
                
                # Basic Info extended
                company.c_contect_address = request.POST.get('c_contect_address', '')
                company.c_wbsite = request.POST.get('c_wbsite', '')
                
                # Owner Info
                company.c_owner_person_fullName = request.POST.get('c_owner_person_fullName', '')
                company.c_owner_person = request.POST.get('c_owner_person', '')
                company.c_owner_person_phone = request.POST.get('c_owner_person_phone', '')
                company.c_owner_person_email = request.POST.get('c_owner_person_email', '')
                
                # Social Links
                company.c_facebook_page = request.POST.get('c_facebook_page', '')
                company.c_twitter_page = request.POST.get('c_twitter_page', '')
                company.c_instegram_page = request.POST.get('c_instegram_page', '')
                company.c_linkdin_page = request.POST.get('c_linkdin_page', '')
                company.c_youtube_page = request.POST.get('c_youtube_page', '')
                company.c_telegram_page = request.POST.get('c_telegram_page', '')
                company.c_whatsapp_page = request.POST.get('c_whatsapp_page', '')
                
                if request.FILES.get('c_logo'):
                    company.c_logo = request.FILES.get('c_logo')
                    
                company.save()
                
                # Update session variables
                request.session['company_name'] = company.c_name
                if company.c_logo:
                    request.session['company_logo'] = company.c_logo.url
                    
                messages.success(request, "Company profile updated successfully!")
            except Exception as e:
                messages.error(request, f"Error updating profile: {e}")
                
            return redirect('companyapp:company_profile')
            
    context = {
        'company': company,
        'total_jobs_posted': jops_DB.objects.filter(j_company_id=company_id).count()
    }
    return render(request, 'companyapp/profile.html', context)

def company_applications(request):
    if 'company_id' not in request.session:
        return redirect('home')
        
    company_id = request.session['company_id']
    company = Company_DB.objects.filter(id=company_id).first()
    
    if not company or not company.c_active:
        if 'company_id' in request.session:
            del request.session['company_id']
        return redirect('home')

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_status':
            try:
                app_id = request.POST.get('app_id')
                new_status = request.POST.get('status')
                
                # Verify application belongs to this company and not already soft-deleted
                application = Application_DB.objects.get(id=app_id, a_job__j_company_id=company_id, a_deleted_by_company=False)
                application.a_status = new_status
                application.save()
                
                messages.success(request, f"Application status updated to {new_status}!")
            except Exception as e:
                messages.error(request, f"Error updating status: {e}")
            return redirect('companyapp:company_applications')

        elif action == 'delete_application':
            try:
                app_id = request.POST.get('app_id')
                # Verify this application belongs to this company
                application = Application_DB.objects.get(id=app_id, a_job__j_company_id=company_id)
                # Soft-delete: hide from company view only, applicant still sees it
                application.a_deleted_by_company = True
                application.save()
                messages.success(request, "Application has been removed from your view.")
            except Exception as e:
                messages.error(request, f"Error removing application: {e}")
            return redirect('companyapp:company_applications')

    # Get applications for this company's jobs (exclude company soft-deleted)
    applications_list = Application_DB.objects.filter(
        a_job__j_company_id=company_id,
        a_deleted_by_company=False
    ).order_by('-a_applied_date')
    
    # Get distinct jobs that have applications
    jobs_with_apps = jops_DB.objects.filter(j_company_id=company_id).order_by('j_title')
    
    context = {
        'applications': applications_list,
        'jobs_list': jobs_with_apps,
        'total_applications': applications_list.count(),
        'pending': applications_list.filter(a_status='pending').count(),
        'reviewed': applications_list.filter(a_status='reviewed').count(),
        'accepted': applications_list.filter(a_status='accepted').count(),
        'rejected': applications_list.filter(a_status='rejected').count(),
    }
    return render(request, 'companyapp/applications.html', context)

def company_logout(request):
    """
    Clears the company session and redirects to coreapp home.
    """
    if 'company_id' in request.session:
        del request.session['company_id']
    if 'company_name' in request.session:
        del request.session['company_name']
    if 'company_logo' in request.session:
        del request.session['company_logo']
        
    # Alternatively use request.session.flush() to clear everything including session cookie
    # request.session.flush() 
    
    return redirect('home')


import re

def clean_location(loc_name):
    if not loc_name:
        return "Not Specified"
    # Somali vowel reduction rule: replace consecutive identical vowels with a single one
    return re.sub(r'([aeiou])\1+', r'\1', str(loc_name).lower()).title()

def company_analyze(request):
    if 'company_id' not in request.session:
        return redirect('home')
        
    company_id = request.session['company_id']
    company = Company_DB.objects.filter(id=company_id).first()
    
    if not company or not company.c_active:
        return redirect('home')
        
    # Applications for this company
    apps = Application_DB.objects.filter(a_job__j_company_id=company_id)
    
    # 1. Job Stats (Applications per job)
    jobs_stats = jops_DB.objects.filter(j_company_id=company_id).annotate(app_count=Count('application_db'))
    job_labels = [job.j_title for job in jobs_stats]
    job_data = [job.app_count for job in jobs_stats]
    
    # 2. Status Stats
    status_counts = apps.values('a_status').annotate(total=Count('a_status'))
    status_labels = [s['a_status'].capitalize() for s in status_counts]
    status_data = [s['total'] for s in status_counts]
    
    # 3. Gender Stats
    gender_counts = apps.values('a_shaqod__s_geneder').annotate(total=Count('a_shaqod__s_geneder'))
    gender_labels = [g['a_shaqod__s_geneder'].capitalize() if g['a_shaqod__s_geneder'] else 'Unknown' for g in gender_counts]
    gender_data = [g['total'] for g in gender_counts]
    
    # 4. Location Stats (with cleanup rule)
    location_raw = apps.values_list('a_current_location', flat=True)
    location_map = {}
    for loc in location_raw:
        cleaned = clean_location(loc)
        location_map[cleaned] = location_map.get(cleaned, 0) + 1
    
    location_labels = list(location_map.keys())
    location_data = list(location_map.values())
    
    total_jobs = jobs_stats.count()
    total_apps = apps.count()
    engagement_score = total_apps / total_jobs if total_jobs > 0 else 0
    
    context = {
        'company': company,
        'job_labels': job_labels,
        'job_data': job_data,
        'status_labels': status_labels,
        'status_data': status_data,
        'gender_labels': gender_labels,
        'gender_data': gender_data,
        'location_labels': location_labels,
        'location_data': location_data,
        'total_jobs': total_jobs,
        'total_apps': total_apps,
        'engagement_score': round(engagement_score, 1),
    }
    return render(request, 'companyapp/company_analyze.html', context)


def company_delete_account(request):
    company_id = request.session.get('company_id')
    if not company_id:
        return redirect('home')
        
    company = Company_DB.objects.filter(id=company_id).first()
    
    if not company or not company.c_active:
        if 'company_id' in request.session:
            del request.session['company_id']
        return redirect('home')
        
    if request.method == 'POST':
        password = request.POST.get('password')
        if password == company.c_password:
            company.delete()
            request.session.flush()
            messages.success(request, 'Your company account has been successfully deleted.')
            return redirect('home')
        else:
            messages.error(request, 'Incorrect password. Account deletion failed.')
            return redirect('companyapp:company_profile')
            
    return redirect('companyapp:company_profile')
