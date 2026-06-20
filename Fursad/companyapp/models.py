from django.db import models
from django.contrib.auth.hashers import make_password
# Create your models here.

class Company_DB(models.Model):
    c_name = models.CharField(max_length=100, blank=True, null=True,help_text="Company Name")
    c_description = models.TextField(blank=True, null=True,help_text="Company Description")
    c_email = models.EmailField(blank=True, null=True,help_text="Company Email",unique=True)
    c_phone = models.CharField(max_length=15, blank=True, null=True,help_text="Company Phone")
    c_username = models.CharField(max_length=100, blank=True, null=True,help_text="Company Username")
    c_password = models.CharField(max_length=100, blank=True, null=True,help_text="Company Password")
    c_joined = models.DateField(auto_now_add=True, help_text="Company Joined Date")
    c_logo = models.ImageField(upload_to='static/company_logos/', max_length=200, blank=True, null=True,help_text="Company Logo")
    c_active = models.BooleanField(default=False, help_text="Company Active")
    c_company_lence = models.ImageField(upload_to='static/company_logos/', max_length=200, blank=True, null=True,help_text="Company_geverment_lencec")
    c_verivaed = models.BooleanField(default=False, help_text="Company Verified")
    c_header_location = models.CharField(max_length=100, blank=True, null=True,help_text="Company Header Location")
    c_contect_address = models.CharField(max_length=255, blank=True, null=True,help_text="Company Contect Address")
    c_owner_person = models.CharField(max_length=100, blank=True, null=True,help_text="Company Owner Person")
    c_owner_person_phone = models.CharField(max_length=15, blank=True, null=True,help_text="Company Owner Person Phone")
    c_owner_person_email = models.EmailField(blank=True, null=True,help_text="Company Owner Person Email")
    c_owner_person_fullName = models.CharField(max_length=100, blank=True, null=True,help_text="Company Owner Person Full Name")
    c_owner_person_docoment= models.FileField(upload_to='static/company_logos/', max_length=200, blank=True, null=True,help_text="uploud like somali nira card or ather docoments that goverment recognized")
    c_wbsite = models.URLField(blank=True, null=True,help_text="Company Website")
    c_facebook_page = models.URLField(blank=True, null=True,help_text="Company Facebook Page")
    c_twitter_page = models.URLField(blank=True, null=True,help_text="Company Twitter Page")
    c_instegram_page = models.URLField(blank=True, null=True,help_text="Company Instegram Page")
    c_linkdin_page = models.URLField(blank=True, null=True,help_text="Company Linkdin Page")
    c_youtube_page = models.URLField(blank=True, null=True,help_text="Company Youtube Page")
    c_telegram_page = models.URLField(blank=True, null=True,help_text="Company Telegram Page")
    c_whatsapp_page = models.URLField(blank=True, null=True,help_text="Company Whatsapp Page")
    
    
    
    def __str__(self):

        return f'{self.c_name}  {self.c_email}'
    

    def save(self, *args, **kwargs):
      
        # if self.c_password and not self.c_password.startswith('pbkdf2_') and not self.c_password.startswith('bcrypt') and not self.c_password.startswith('argon2'):
        #     from django.contrib.auth.hashers import make_password
        #     self.c_password = make_password(self.c_password)
            
        
        if not self.c_owner_person_fullName or not self.c_owner_person_email or not self.c_owner_person_phone or not self.c_owner_person_docoment:
            self.c_verivaed = False
            
        super().save(*args, **kwargs)

 
        
        
        

    @property
    def total_jobs(self):
        from jobsapp.models import jops_DB
        return jops_DB.objects.filter(j_company=self).count()

    @property
    def total_applications(self):
        from applications.models import Application_DB
        return Application_DB.objects.filter(a_job__j_company=self).count()

    @property
    def total_hired(self):
        from applications.models import Application_DB
        return Application_DB.objects.filter(a_job__j_company=self, a_status='accepted').count()

    class Meta:
        verbose_name = "Combani"
        verbose_name_plural = "combaniyo"
        unique_together = ("c_username", "c_email")





