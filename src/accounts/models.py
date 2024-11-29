from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    vault_path = models.CharField(max_length=255)
    access_token = models.CharField(max_length=255)
    last_synced = models.DateTimeField(null=True, blank=True)
