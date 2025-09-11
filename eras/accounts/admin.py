from django.contrib import admin

from .models import User, CitizenProfile
admin.site.register(User)   
admin.site.register(CitizenProfile)

# Register your models here.
