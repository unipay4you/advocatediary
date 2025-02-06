from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin


# Register your models here.

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'user_name', 'user_type']

admin.site.register(CustomUser,CustomUserAdmin)
admin.site.register(User_ID)
admin.site.register(State)
admin.site.register(District)
admin.site.register(Bar)
admin.site.register(user_login_details)
admin.site.register(Case_Stage)
admin.site.register(Case_Type)
admin.site.register(Court_Type)
admin.site.register(Court)
admin.site.register(Clients)
admin.site.register(Case_Master)
admin.site.register(Associate_With_Client)
admin.site.register(CaseHistory)


