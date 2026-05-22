from django.contrib import admin

# Register your models here.

from .models import shaqod_DB

class shaqoAdmin(admin.ModelAdmin):
    list_display = ('s_fullname', 's_email', 's_status')
    list_filter = ('s_status', 's_created')
    search_fields = ('s_fullname', 's_email')

admin.site.register(shaqod_DB, shaqoAdmin)