from django.contrib import admin

from .models import *

admin.site.register(UserBase)
admin.site.register(Role)
admin.site.register(Permission)
