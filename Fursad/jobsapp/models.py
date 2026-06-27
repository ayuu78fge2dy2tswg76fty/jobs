from django.db import models

# Create your models here.

from companyapp.models import Company_DB

class jops_DB(models.Model):
    jobtype =[
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship')
    ]
    j_title = models.CharField(max_length=100, blank=True, null=True,help_text="Job Title")
    j_description = models.TextField(blank=True, null=True,help_text="Job Description")
    j_company = models.ForeignKey(Company_DB, on_delete=models.CASCADE, help_text="Company")
    j_location = models.CharField(max_length=100, blank=True, null=True,help_text="Job Location")
    j_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,help_text="Job Salary")
    j_posted = models.DateTimeField(auto_now_add=True, help_text="Job Posted Date")
    j_active = models.BooleanField(default=False, help_text="Job Active")
    j_logo = models.ImageField(upload_to='static/job_logos/', max_length=200, blank=True, null=True,help_text="Job Logo")
    j_jobtype = models.CharField(max_length=20, choices=jobtype, blank=True, null=True, help_text="Job Type")
    j_EXP = models.DateField(help_text="Job Experience")

    def __str__(self):
        return f'{self.j_title}  {self.j_company}'
        
        

    class Meta:
        verbose_name = "SHaqo"
        verbose_name_plural = "SHaqoyin"

