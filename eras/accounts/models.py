from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER_TYPES = (
        ('citizen', 'Citizen'),
        ('service_provider', 'Service Provider'),
    )

    user_type = models.CharField(
        max_length=20, choices=USER_TYPES, default='citizen')
    phone_number = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return self.username
