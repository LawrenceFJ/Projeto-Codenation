from django.contrib import admin
from .models import Group, User, Agent, ErrorLog

# Register your models here.

admin.site.register(User)
admin.site.register(Agent)
admin.site.register(ErrorLog)
