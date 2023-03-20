from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import Subscriptions, User


class UserAdmin(admin.ModelAdmin):
    list_filter = ('email', 'username')

admin.site.register(User, UserAdmin)
admin.site.register(Subscriptions)