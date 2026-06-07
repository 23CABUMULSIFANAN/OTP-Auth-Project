
from django.contrib import admin
from .models import CustomUser, OTPToken

admin.site.register(CustomUser)
admin.site.register(OTPToken)
