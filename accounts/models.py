from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.conf import settings


class CustomUserManager(UserManager):
    
    def get_user_by_email(self, email):
        user = None
        try:
            user = self.get(email=email)
        except CustomUser.DoesNotExist:
            pass
        return user
    

class CustomUser(AbstractUser):
    objects = CustomUserManager()


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=250, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.user.username} profile"
    
    
