from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    preferences = models.JSONField(default=dict, blank=True, null=True, help_text="User preferences for topics, sources, etc.")

    def __str__(self):
        return self.username
