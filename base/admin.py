from django.contrib import admin
from .models import User, IFTAR, Notification

# Register your models here.

admin.site.register(User)
admin.site.register(IFTAR)
admin.site.register(Notification)