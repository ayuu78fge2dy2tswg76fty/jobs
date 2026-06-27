from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Count, Q
from .models import shaqod_DB
from applications.models import Application_DB
from jobsapp.models import jops_DB

# Create your views here.

def shaqodon_dashboard(request):
    if 'shaqodon_id' not in request.session:
        return redirect('home')
        
    shaqodon_id = request.session['shaqodon_id']
    shaqodon = shaqod_DB.objects.filter(id=shaqodon_id).first()
    
    if not shaqodon or not shaqodon.s_status:
        if 'shaqodon_id' in request.session:
            del request.session['shaqodon_id']
        messages.error(request, 'Your account is deactivated.')
        return redirect('home')
        
    # Real data from DB
    my_applications = Application_DB.objects.filter(a_shaqod=shaqodon)
    total_apps = my_applications.count()
    shortlisted = my_applications.filter(a_status='accepted').count()
    rejected = my_applications.filter(a_status='rejected').count()
    pending = my_applications.filter(a_status='pending').count()

    # Profile Strength calculation
    strength = 20  # Base strength for registration
    if shaqodon.s_fullname: strength += 20
    if shaqodon.s_phone: strength += 20
    if shaqodon.s_profile_img: strength += 20
    if my_applications.exists(): strength += 20

    # Top 3 Companies (Based on job count and activity)
    from companyapp.models import Company_DB
    top_companies = Company_DB.objects.filter(c_active=True).annotate(
        job_count=Count('jops_db', distinct=True),
        accepted_count=Count('jops_db__application_db', filter=Q(jops_db__application_db__a_status='accepted'), distinct=True)
    ).order_by('-job_count', '-accepted_count')[:3]

    # Recent Posted Jobs
    recent_jobs = jops_DB.objects.filter(j_active=True, j_company__c_active=True).order_by('-j_posted')[:3]
    
    recent_applications = my_applications.order_by('-a_applied_date')[:5]
        
    context = {
        'shaqodon': shaqodon,
        'total_apps': total_apps,
        'shortlisted': shortlisted,
        'rejected': rejected,
        'pending': pending,
        'recent_applications': recent_applications,
        'strength': strength,
        'top_companies': top_companies,
        'recent_jobs': recent_jobs,
    }
    return render(request, 'shaqodonapp/dashboard.html', context)

def shaqodon_login(request):
    if request.method == 'POST':
        identifier = request.POST.get('identifier')
        password = request.POST.get('password')
        
        shaqodon = shaqod_DB.objects.filter(s_email=identifier).first()
        if not shaqodon:
            shaqodon = shaqod_DB.objects.filter(s_username=identifier).first()
            
        if shaqodon and shaqodon.s_password == password:
            if shaqodon.s_status:
                request.session['shaqodon_id'] = shaqodon.id
                request.session['shaqodon_username'] = shaqodon.s_username
                request.session['shaqodon_fullname'] = shaqodon.s_fullname
                if shaqodon.s_profile_img:
                    request.session['shaqodon_img'] = shaqodon.s_profile_img.url
                
                messages.success(request, f'Welcome back, {shaqodon.s_fullname}!')
                return redirect('shaqodonapp:shaqodon_dashboard')
            else:
                messages.warning(request, 'Your account is pending activation.')
                return redirect(request.META.get('HTTP_REFERER', 'home'))
        else:
            messages.error(request, 'Invalid email/username or password.')
            return redirect(request.META.get('HTTP_REFERER', 'home'))
            
    return redirect('home')

def shaqodon_register(request):
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        gender = request.POST.get('gender', 'male')
        
        address = request.POST.get('address')
        education = request.POST.get('education')
        skills = request.POST.get('skills')
        experience = request.POST.get('experience')
        cv = request.FILES.get('cv')
        profile_img = request.FILES.get('profile_img')
        
        if shaqod_DB.objects.filter(s_email=email).exists() or shaqod_DB.objects.filter(s_username=username).exists():
            messages.error(request, 'Email or Username already exists.')
        elif shaqod_DB.objects.filter(s_phone=phone).exists():
            messages.error(request, 'Phone number already exists. Please use a different one.')
        else:
            new_shaqodon = shaqod_DB.objects.create(
                s_fullname=fullname,
                s_email=email,
                s_username=username,
                s_password=password,
                s_phone=phone,
                s_geneder=gender,
                s_address=address,
                s_education=education,
                s_skills=skills,
                s_experience=experience,
                s_cv=cv,
                s_profile_img=profile_img,
                s_status=True
            )
            
            # Automatically log the user in
            request.session['shaqodon_id'] = new_shaqodon.id
            request.session['shaqodon_username'] = new_shaqodon.s_username
            request.session['shaqodon_fullname'] = new_shaqodon.s_fullname
            if new_shaqodon.s_profile_img:
                request.session['shaqodon_img'] = new_shaqodon.s_profile_img.url
            
            messages.success(request, 'Account created successfully! Welcome to your dashboard.')
            return redirect('shaqodonapp:shaqodon_dashboard')
            
        return redirect(request.META.get('HTTP_REFERER', 'home'))
    return redirect('home')

def shaqodon_logout(request):
    if 'shaqodon_id' in request.session:
        del request.session['shaqodon_id']
    if 'shaqodon_username' in request.session:
        del request.session['shaqodon_username']
    if 'shaqodon_fullname' in request.session:
        del request.session['shaqodon_fullname']
    if 'shaqodon_img' in request.session:
        del request.session['shaqodon_img']
        
    return redirect('home')

def shaqodon_profile(request):
    if 'shaqodon_id' not in request.session:
        return redirect('home')
    
    shaqodon_id = request.session['shaqodon_id']
    shaqodon = shaqod_DB.objects.get(id=shaqodon_id)
    
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        education = request.POST.get('education')
        skills = request.POST.get('skills')
        experience = request.POST.get('experience')
        cv = request.FILES.get('cv')
        image = request.FILES.get('profile_img')
        
        shaqodon.s_fullname = fullname
        shaqodon.s_email = email
        shaqodon.s_phone = phone
        shaqodon.s_address = address
        shaqodon.s_education = education
        shaqodon.s_skills = skills
        shaqodon.s_experience = experience
        if cv:
            shaqodon.s_cv = cv
        if image:
            shaqodon.s_profile_img = image

        # Handle password change
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        if new_password:
            if new_password == confirm_password:
                shaqodon.s_password = new_password
            else:
                messages.error(request, "New passwords do not match. Profile saved, but password was NOT changed.")
                shaqodon.save()
                request.session['shaqodon_fullname'] = shaqodon.s_fullname
                if shaqodon.s_profile_img:
                    request.session['shaqodon_img'] = shaqodon.s_profile_img.url
                return redirect('shaqodonapp:shaqodon_profile')
            
        shaqodon.save()
        
        # Update session data
        request.session['shaqodon_fullname'] = shaqodon.s_fullname
        if shaqodon.s_profile_img:
            request.session['shaqodon_img'] = shaqodon.s_profile_img.url
            
        messages.success(request, "Profile updated successfully!")
        return redirect('shaqodonapp:shaqodon_profile')
        
    return render(request, 'shaqodonapp/myprofile.html', {'shaqodon': shaqodon})

def shaqodon_applications(request):
    if 'shaqodon_id' not in request.session:
        return redirect('home')
    shaqodon_id = request.session['shaqodon_id']
    applications = Application_DB.objects.filter(a_shaqod_id=shaqodon_id).order_by('-a_applied_date')
    
    # Calculate Stats
    total = applications.count()
    accepted = applications.filter(a_status='accepted').count()
    pending = applications.filter(a_status='pending').count()
    rejected = applications.filter(a_status='rejected').count()
    
    return render(request, 'shaqodonapp/myapplications.html', {
        'applications': applications,
        'total': total,
        'accepted': accepted,
        'pending': pending,
        'rejected': rejected
    })

def shaqodon_jobs(request):
    if 'shaqodon_id' not in request.session:
        return redirect('home')
    
    query = request.GET.get('q', '')
    location = request.GET.get('location', '')
    job_type = request.GET.get('type', '')
    company_id = request.GET.get('company', '')
    
    jobs = jops_DB.objects.filter(j_active=True, j_company__c_active=True)
    
    if query:
        jobs = jobs.filter(
            Q(j_title__icontains=query) | 
            Q(j_description__icontains=query) | 
            Q(j_company__c_name__icontains=query)
        )
    
    if location:
        jobs = jobs.filter(j_location__icontains=location)
        
    if job_type:
        jobs = jobs.filter(j_jobtype=job_type)
        
    if company_id:
        jobs = jobs.filter(j_company_id=company_id)
        
    jobs = jobs.order_by('-j_posted')
    
    # Get filter options
    locations = jops_DB.objects.filter(j_active=True, j_company__c_active=True).values_list('j_location', flat=True).distinct()
    from companyapp.models import Company_DB
    companies = Company_DB.objects.filter(c_active=True)
    
    context = {
        'jobs': jobs,
        'locations': locations,
        'companies': companies,
        'query': query,
        'selected_location': location,
        'selected_type': job_type,
        'selected_company': company_id,
    }
    return render(request, 'shaqodonapp/jobs.html', context)

def shaqodon_companies(request):
    if 'shaqodon_id' not in request.session:
        return redirect('home')
    from companyapp.models import Company_DB
    companies = Company_DB.objects.filter(c_active=True)
    return render(request, 'shaqodonapp/companies.html', {'companies': companies})

def shaqodon_company_detail(request, company_id):
    if 'shaqodon_id' not in request.session:
        return redirect('home')
    from companyapp.models import Company_DB
    from jobsapp.models import jops_DB
    
    company = Company_DB.objects.filter(id=company_id, c_active=True).first()
    if not company:
        messages.error(request, "This company is currently unavailable.")
        return redirect('shaqodonapp:shaqodon_companies')
    jobs = jops_DB.objects.filter(j_company=company, j_active=True).order_by('-j_posted')
    
    return render(request, 'shaqodonapp/company_detail.html', {
        'company': company,
        'jobs': jobs
    })

def shaqodon_job_detail(request, job_id):
    if 'shaqodon_id' not in request.session:
        return redirect('home')
    
    job = jops_DB.objects.filter(id=job_id, j_active=True, j_company__c_active=True).first()
    if not job:
        messages.error(request, "This job is currently unavailable.")
        return redirect('shaqodonapp:shaqodon_jobs')
    shaqodon_id = request.session['shaqodon_id']
    shaqodon = shaqod_DB.objects.get(id=shaqodon_id)
    
    # Check if already applied
    has_applied = Application_DB.objects.filter(a_job=job, a_shaqod=shaqodon).exists()
    
    if request.method == 'POST':
        # Handle application submission
        cv = request.FILES.get('cv')
        cover_letter = request.POST.get('cover_letter')
        location = request.POST.get('location')
        
        # Fallback to profile CV if no new CV is uploaded
        if not cv:
            cv = shaqodon.s_cv
            
        if not cv:
            messages.error(request, "Please upload your CV or add one to your profile.")
            return redirect('shaqodonapp:shaqodon_job_detail', job_id=job_id)
            
        Application_DB.objects.create(
            a_job=job,
            a_shaqod=shaqodon,
            a_cv=cv,
            a_cover_letter=cover_letter,
            a_current_location=location,
            a_status='pending'
        )
        messages.success(request, "Application submitted successfully!")
        return redirect('shaqodonapp:shaqodon_applications')

    return render(request, 'shaqodonapp/jobsdetail.html', {
        'job': job,
        'shaqodon': shaqodon,
        'has_applied': has_applied
    })

def edit_application(request, app_id):
    if 'shaqodon_id' not in request.session:
        return redirect('home')
        
    application = Application_DB.objects.get(id=app_id)
    
    # Security: Ensure this app belongs to the logged in shaqodon
    if application.a_shaqod_id != request.session['shaqodon_id']:
        messages.error(request, "Unauthorized action.")
        return redirect('shaqodonapp:shaqodon_applications')
        
    # Condition: Only edit if pending
    if application.a_status != 'pending':
        messages.error(request, "You cannot edit an application that is already being reviewed.")
        return redirect('shaqodonapp:shaqodon_applications')
        
    if request.method == 'POST':
        cover_letter = request.POST.get('cover_letter')
        location = request.POST.get('location')
        cv = request.FILES.get('cv')
        
        application.a_cover_letter = cover_letter
        application.a_current_location = location
        if cv:
            application.a_cv = cv
            
        application.save()
        messages.success(request, "Application updated successfully!")
        return redirect('shaqodonapp:shaqodon_applications')
        
    return redirect('shaqodonapp:shaqodon_applications')

def delete_application(request, app_id):

    if 'shaqodon_id' not in request.session:
        return redirect('home')
    
    if request.method == 'POST':
        try:
            application = Application_DB.objects.get(id=app_id, a_shaqod_id=request.session['shaqodon_id'])
            application.delete()  
            messages.success(request, "Application has been permanently deleted.")
        except Application_DB.DoesNotExist:
            messages.error(request, "Application not found or you don't have permission to delete it.")
        except Exception as e:
            messages.error(request, f"Error deleting application: {e}")
    
    return redirect('shaqodonapp:shaqodon_applications')

def shaqodon_delete_account(request):
    if 'shaqodon_id' not in request.session:
        return redirect('home')
    
    if request.method == 'POST':
        try:
            shaqodon = shaqod_DB.objects.get(id=request.session['shaqodon_id'])
            shaqodon.delete()
            
            # Clear session
            if 'shaqodon_id' in request.session:
                del request.session['shaqodon_id']
            if 'shaqodon_username' in request.session:
                del request.session['shaqodon_username']
            if 'shaqodon_fullname' in request.session:
                del request.session['shaqodon_fullname']
            if 'shaqodon_img' in request.session:
                del request.session['shaqodon_img']
                
            messages.success(request, "Your account has been deleted permanently.")
        except Exception as e:
            messages.error(request, f"Error deleting account: {e}")
            
    return redirect('home')
