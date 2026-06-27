from django.db import models

# Create your models here.

from shaqodonapp.models import shaqod_DB
from jobsapp.models import jops_DB



class Application_DB(models.Model):
    a_job = models.ForeignKey(jops_DB, on_delete=models.CASCADE, help_text="Job Title")
    a_shaqod = models.ForeignKey(shaqod_DB, on_delete=models.CASCADE, help_text="Shaqod Qofka")
    a_cv = models.FileField(upload_to='static/cv/', help_text="Upload CV")
    a_cover_letter = models.TextField(blank=True, null=True, help_text="Cover Letter")
    a_applied_date = models.DateTimeField(auto_now_add=True, help_text="Application Date")
    a_current_location = models.CharField(max_length=100, blank=True, null=True, help_text="Current Location")
    a_status_choices = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    a_status = models.CharField(max_length=20, choices=a_status_choices, default='pending')
    a_deleted_by_company = models.BooleanField(default=False, help_text="Company soft-deleted this application (hidden from company view only)")

    def __str__(self):
        return f'{self.a_shaqod.s_fullname}  {self.a_job.j_title}'

    class Meta:
        verbose_name = "Application"    
        verbose_name_plural = "Applications"
