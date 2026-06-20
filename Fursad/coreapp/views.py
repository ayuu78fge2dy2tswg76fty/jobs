from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import json

from companyapp.models import Company_DB
from jobsapp.models import jops_DB
from coreapp.models import PasswordResetOTP

# Create your views here.

def home(request):
    return render(request, 'coreapp/home.html')


def about(request):
    return render(request, 'coreapp/about.html')


from applications.models import Application_DB

def companies(request):
    query = request.GET.get('q', '')
    companies_list = Company_DB.objects.filter(c_verivaed=True)
    if query:
        companies_list = companies_list.filter(Q(c_name__icontains=query) | Q(c_description__icontains=query))
        
    return render(request, 'coreapp/companies.html', {'companies': companies_list, 'query': query})


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
        description = request.POST.get('description')
        phone = request.POST.get('phone')
        header_location = request.POST.get('header_location')
        logo = request.FILES.get('logo')
        company_lence = request.FILES.get('company_lence')
        owner_name = request.POST.get('owner_name')
        owner_email = request.POST.get('owner_email')
        owner_phone = request.POST.get('owner_phone')
        owner_document = request.FILES.get('owner_document')
        
        if Company_DB.objects.filter(c_email=email).exists() or Company_DB.objects.filter(c_username=username).exists():
            messages.error(request, 'Email or Username already exists')
        else:
            Company_DB.objects.create(
                c_name=name,
                c_email=email,
                c_username=username,
                c_password=password,
                c_description=description,
                c_phone=phone,
                c_header_location=header_location,
                c_logo=logo,
                c_company_lence=company_lence,
                c_owner_person_fullName=owner_name,
                c_owner_person_email=owner_email,
                c_owner_person_phone=owner_phone,
                c_owner_person_docoment=owner_document,
                c_active=False
            )
            import json
            success_data = {
                'name': name,
                'email': email,
                'phone': phone
            }
            messages.success(request, f"REG_SUCCESS|{json.dumps(success_data)}")
            
        return redirect(request.META.get('HTTP_REFERER', 'home'))
    else:
        return redirect('home')


@require_POST
def forgot_password_request(request):
    """Step 1: Generate 6-digit OTP and send it via email."""
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        user_type = data.get('user_type', 'company')
    except Exception:
        return JsonResponse({'success': False, 'message': 'Invalid request.'}, status=400)

    if not email:
        return JsonResponse({'success': False, 'message': 'Email is required.'}, status=400)

    # Verify user exists
    user_exists = False
    if user_type == 'company':
        user_exists = Company_DB.objects.filter(c_email__iexact=email).exists()
    elif user_type == 'shaqodon':
        from shaqodonapp.models import shaqod_DB
        user_exists = shaqod_DB.objects.filter(s_email__iexact=email).exists()

    if not user_exists:
        return JsonResponse({'success': False, 'message': 'No account found with this email.'}, status=404)

    # Delete any old OTPs for this email
    PasswordResetOTP.objects.filter(email__iexact=email, user_type=user_type, is_used=False).delete()

    # Generate new OTP
    otp = PasswordResetOTP.generate_otp()
    PasswordResetOTP.objects.create(email=email, otp=otp, user_type=user_type)

    # Build premium HTML email
    html_message = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Fursad - Password Reset</title>
      <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    </head>
    <body style="margin:0;padding:0;background:#0f172a;font-family:'Segoe UI',Arial,sans-serif;">
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f172a;min-height:100vh;padding:40px 0;">
        <tr>
          <td align="center">
            <table width="560" cellpadding="0" cellspacing="0" style="background:linear-gradient(135deg,#1e293b 0%,#0f172a 100%);border-radius:20px;border:1px solid #334155;overflow:hidden;">
              <!-- Header -->
              <tr>
                <td style="background:linear-gradient(90deg,#3b82f6,#10b981);padding:32px;text-align:center;">
                  <div style="font-size:2rem;font-weight:800;color:#ffffff;letter-spacing:-0.5px;">
                    <i class="fa-solid fa-briefcase"></i> Fursad
                  </div>
                  <div style="color:rgba(255,255,255,0.85);margin-top:6px;font-size:0.95rem;letter-spacing:1px;text-transform:uppercase;">
                    Password Reset Request
                  </div>
                </td>
              </tr>
              <!-- Body -->
              <tr>
                <td style="padding:40px 40px 20px 40px;">
                  <p style="color:#94a3b8;font-size:1rem;margin:0 0 24px 0;line-height:1.6;">
                    Hello! We received a request to reset the password for your <strong style="color:#e2e8f0;">Fursad</strong> account. Use the verification code below to proceed.
                  </p>
                  <!-- OTP Box -->
                  <div style="background:linear-gradient(135deg,rgba(59,130,246,0.15),rgba(16,185,129,0.1));border:2px solid rgba(59,130,246,0.4);border-radius:16px;padding:32px;text-align:center;margin:0 0 28px 0;">
                    <div style="color:#94a3b8;font-size:0.85rem;letter-spacing:2px;text-transform:uppercase;margin-bottom:12px;">Your Verification Code</div>
                    <div style="font-size:3rem;font-weight:900;letter-spacing:12px;color:#ffffff;font-family:'Courier New',monospace;text-shadow:0 0 30px rgba(59,130,246,0.6);">
                      {otp}
                    </div>
                    <div style="color:#64748b;font-size:0.8rem;margin-top:12px;">&#8987; Expires in <strong style="color:#f59e0b;">10 minutes</strong></div>
                  </div>
                  <!-- Warning -->
                  <div style="background:rgba(245,158,11,0.1);border-left:4px solid #f59e0b;border-radius:8px;padding:14px 18px;margin-bottom:28px;">
                    <p style="color:#fbbf24;margin:0;font-size:0.88rem;line-height:1.5;">
                      &#9888; If you did not request a password reset, please ignore this email. Your account remains secure.
                    </p>
                  </div>
                  <p style="color:#64748b;font-size:0.85rem;line-height:1.6;margin:0;">
                    For security, this code can only be used once and will expire in 10 minutes.
                  </p>
                </td>
              </tr>
              <!-- Footer -->
              <tr>
                <td style="padding:24px 40px 32px 40px;border-top:1px solid #1e293b;">
                  <p style="color:#475569;font-size:0.8rem;margin:0;text-align:center;">
                    &copy; 2026 Fursad &mdash;Somali Job Portal &bull; Somalia
                  </p>
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """

    plain_message = f"Your Fursad password reset code is: {otp}\nThis code expires in 10 minutes."

    try:
        send_mail(
            subject='🔐 Fursad - Your Password Reset Code',
            message=plain_message,
            from_email=None,  # Uses DEFAULT_FROM_EMAIL from settings
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Failed to send email. Please try again. ({str(e)})'}, status=500)

    return JsonResponse({'success': True, 'message': f'A 6-digit code has been sent to {email}.'})


@require_POST
def forgot_password_reset(request):
    """Step 2: Verify OTP and update password."""
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        otp = data.get('otp', '').strip()
        new_password = data.get('new_password', '').strip()
        user_type = data.get('user_type', 'company')
    except Exception:
        return JsonResponse({'success': False, 'message': 'Invalid request.'}, status=400)

    if not all([email, otp, new_password]):
        return JsonResponse({'success': False, 'message': 'All fields are required.'}, status=400)

    if len(new_password) < 6:
        return JsonResponse({'success': False, 'message': 'Password must be at least 6 characters.'}, status=400)

    # Find the OTP record
    try:
        otp_record = PasswordResetOTP.objects.filter(
            email__iexact=email,
            otp=otp,
            user_type=user_type,
            is_used=False
        ).latest('created_at')
    except PasswordResetOTP.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Invalid or expired code. Please request a new one.'}, status=400)

    if not otp_record.is_valid():
        return JsonResponse({'success': False, 'message': 'This code has expired. Please request a new one.'}, status=400)

    # Update password
    if user_type == 'company':
        updated = Company_DB.objects.filter(c_email__iexact=email).update(c_password=new_password)
        if not updated:
            return JsonResponse({'success': False, 'message': 'Account not found.'}, status=404)
    elif user_type == 'shaqodon':
        from shaqodonapp.models import shaqod_DB
        updated = shaqod_DB.objects.filter(s_email__iexact=email).update(s_password=new_password)
        if not updated:
            return JsonResponse({'success': False, 'message': 'Account not found.'}, status=404)
    else:
        return JsonResponse({'success': False, 'message': 'Invalid user type.'}, status=400)

    # Mark OTP as used
    otp_record.is_used = True
    otp_record.save()

    return JsonResponse({'success': True, 'message': 'Password updated successfully! You can now log in.'})
