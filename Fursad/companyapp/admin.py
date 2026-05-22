from django.contrib import admin

# Register your models here.

from.models import Company_DB

class companyAdmin(admin.ModelAdmin):
    list_display = ('c_name', 'c_email', 'c_phone', 'c_username', 'c_joined', 'c_active')
    list_filter = ('c_active', 'c_joined')
    search_fields = ('c_name', 'c_email', 'c_username')

admin.site.register(Company_DB, companyAdmin)