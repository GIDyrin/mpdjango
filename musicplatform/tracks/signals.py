from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Playlist

User = get_user_model()

@receiver(post_save, sender=User)
def create_system_playlist(sender, instance, created, **kwargs):
    if created:
        Playlist.objects.create(
            user=instance,
            name="System Playlist",
            is_system=True
        )