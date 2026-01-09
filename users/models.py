from django.db import models
from django.contrib.auth.models import AbstractBaseUser


class User(AbstractBaseUser):
    name = models.CharField(max_length=250)
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        primary_key=True,
    )

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
