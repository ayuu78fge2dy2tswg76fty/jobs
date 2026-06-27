from django.contrib import admin

# Register your models here.

from .models import Application_DB

class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('a_job', 'a_shaqod', 'a_status')
    list_filter = ('a_status', 'a_applied_date')
    search_fields = ('a_job', 'a_shaqod')

admin.site.register(Application_DB, ApplicationAdmin)
admin.site.site_header = "Furad Admin"

