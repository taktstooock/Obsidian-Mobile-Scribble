from django.db import models
from accounts.models import User
from django.utils import timezone

def _get_current_time():
    # Return current time without microseconds
    # since microseconds are not saved in the vault
    return timezone.now().replace(microsecond=0)

class Memo(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memos')
    created_at = models.DateTimeField(default=_get_current_time)
    updated_at = models.DateTimeField(auto_now=True)
    vault_synced_at = models.DateTimeField(null=True, blank=True)