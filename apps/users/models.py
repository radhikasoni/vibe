from django.db import models
from django.contrib.auth.models import User

# Create your models here.


ROLE_CHOICES = (
    ('admin'  , 'Admin'),
    ('user'  , 'User'),
)

STATUS_CHOICES = (
    ('active', 'Active'),
    ('suspended', 'Suspended'),
    ('deleted', 'Deleted'),
    ('logged_out', 'Logged Out'),
)

class Profile(models.Model):
    user      = models.OneToOneField(User, on_delete=models.CASCADE)
    role      = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    country   = models.CharField(max_length=255, null=True, blank=True)
    city      = models.CharField(max_length=255, null=True, blank=True)
    zip_code  = models.CharField(max_length=255, null=True, blank=True)
    address   = models.CharField(max_length=255, null=True, blank=True)
    phone     = models.CharField(max_length=255, null=True, blank=True)
    avatar    = models.ImageField(upload_to='avatar', null=True, blank=True)

    # Apple login fields
    apple_id = models.CharField(max_length=255, null=True, blank=True, unique=True)
    is_apple_user = models.BooleanField(default=False)

    # User status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return self.user.username