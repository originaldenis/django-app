from django.contrib.auth.models import User
from django.db import models


def avatar_image_directory_path(instanse: "Profile", filename: str) -> str:
    return f"profiles/{instanse.user.id}_profile/avatar/{filename}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    agreement_accepted = models.BooleanField(default=False)
    avatar = models.ImageField(blank=True, upload_to=avatar_image_directory_path)
