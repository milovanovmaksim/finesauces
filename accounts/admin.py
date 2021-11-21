from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin

from .models import Profile


CustomUser = get_user_model()


class CustomUserAdmin(UserAdmin):
    model = CustomUser


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'address', 'postal_code', 'city']


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin)