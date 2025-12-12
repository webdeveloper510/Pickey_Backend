from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
import uuid
from .managers import CustomUserManager
# Create your models here.

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)

    class Meta:
        abstract = True

class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    USER_TYPES = (
        (1, 'SuperAdmin'),
        (2, 'Admin'),
        (3, 'User'),
    )
    GENDER_CHOICES = (
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    )
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=100)
    display_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100,null=True)
    user_type = models.IntegerField(choices=USER_TYPES)
    profile_image = models.ImageField(upload_to='user_images/', null=True, blank=True)
    verification_token = models.CharField(max_length=100, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15,null=True, blank=True)
    apple_id = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    avatar_url = models.URLField(blank=True, null=True)
    pickey_id = models.CharField(max_length=50, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)

    objects = CustomUserManager()
    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email
    
    
    
    
class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_otps')
    otp = models.IntegerField()
    expires_at = models.DateTimeField()
    otp_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)    
    
    
    


    