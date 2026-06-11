from django.db import models

# Create your models here.

from jobsapp.models import jops_DB

class shaqod_DB(models.Model):
    eductaion_chiece =[
       ( 'High School', 'High School'),
        ( 'Bachelor', 'Bachelor'),
        ( 'Master', 'Master'),
        ( 'PhD', 'PhD'),
        ('Other', 'Other'),
        ('Experience', 'Experience')
    ]
    s_fullname = models.CharField(max_length=100, help_text="Full Name")
    s_email = models.EmailField(unique=True, help_text="Email")
    s_username = models.CharField(max_length=100, unique=True, help_text="Username")
    s_password = models.CharField(max_length=100, help_text="Password")
    s_phone = models.CharField(max_length=15, unique=True, blank=True, null=True, help_text="Phone")
    s_profile_img = models.ImageField(upload_to='shaqodonapp/profile/', blank=True, null=True, help_text="Profile Image")
    s_status = models.BooleanField(default=True)
    s_geneder = models.CharField(max_length=10, choices=[('male', 'Male'),('female', 'Female'),], default='male')
    s_created = models.DateTimeField(auto_now_add=True, help_text="Created Date")
    s_address = models.CharField(max_length=255, blank=True, null=True)
    s_cv = models.FileField(upload_to='shaqodonapp/cv/', blank=True, null=True)
    s_experience = models.TextField(blank=True, null=True)
    s_skills = models.TextField(blank=True, null=True)
    s_education = models.CharField(max_length=100, choices=eductaion_chiece, blank=True, null=True)
    def __str__(self):
        return f'{self.s_fullname}  {self.s_email}'
        
    class Meta:
        verbose_name = 'Shaqodon'
        verbose_name_plural = 'Shaqodonayal'