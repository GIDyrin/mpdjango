from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Playlist, User

@receiver(post_save, sender=User)
def create_system_playlist(sender, instance, created, **kwargs):
    if created:
        # Проверяем, существует ли уже системный плейлист для пользователя
        existing_playlist = Playlist.objects.filter(user=instance, is_system=True).first()
        if not existing_playlist:
            Playlist.objects.create(
                user=instance,
                name="System Playlist",
                is_system=True
            )