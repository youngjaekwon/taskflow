import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from users.managers import CustomUserManager


def profile_image_upload_to(instance, filename):
    return f"profile_images/{instance.id}/{filename}"


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    profile_image = models.ImageField(
        upload_to=profile_image_upload_to,
        null=True,
        blank=True,
    )
    email_verified = models.BooleanField(default=False)
    username = models.CharField(max_length=150, unique=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = f"user_{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email
