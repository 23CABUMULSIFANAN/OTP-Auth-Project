from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class CustomUserManager(BaseUserManager):

    def create_user(self, email, name, phone, password=None):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, phone=phone)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, phone, password):
        user = self.create_user(email, name, phone, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    
    ROLE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')  # ← add this
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone']

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email} ({self.role})"

class OTPToken(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='otps')
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email} - {self.otp_code}"
    
class SavedProperty(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='saved_properties')
    property_id = models.IntegerField()
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    price = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    image = models.URLField()
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'property_id']

    def __str__(self):
        return f"{self.user.email} - {self.title}"
    
class UserProperty(models.Model):
    STATUS_CHOICES = [
        ('For Sale', 'For Sale'),
        ('For Rent', 'For Rent'),
    ]
    TYPE_CHOICES = [
        ('Apartment', 'Apartment'),
        ('Villa', 'Villa'),
        ('Commercial', 'Commercial'),
        ('Penthouse', 'Penthouse'),
        ('Plot', 'Plot'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='properties')
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    price = models.CharField(max_length=100)
    property_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    beds = models.IntegerField(default=0)
    baths = models.IntegerField(default=1)
    sqft = models.CharField(max_length=50)
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.title}"