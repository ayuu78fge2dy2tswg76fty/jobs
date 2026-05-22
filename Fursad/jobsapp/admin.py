from django.contrib import admin

# Register your models here.

from .models import jops_DB

class jobsAdmin(admin.ModelAdmin):
    list_display = ('j_title', 'j_company', 'j_location')
    list_filter = ('j_company', 'j_location')
    search_fields = ('j_title', 'j_company', 'j_location')

admin.site.register(jops_DB, jobsAdmin)