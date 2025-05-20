from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Playlist, User, Track
import shutil
import os
from django.conf import settings

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


import logging
logger = logging.getLogger(__name__)

@receiver(pre_delete, sender=Track)
def delete_track_files(sender, instance, **kwargs):
    try:
        if instance.hls_playlist:
            hls_dir = os.path.join(settings.MEDIA_ROOT, 'hls/', os.path.dirname(instance.hls_playlist))
            if os.path.exists(hls_dir):
                logger.info(f"Deleting HLS directory: {hls_dir}")
                shutil.rmtree(hls_dir, ignore_errors=True)
            else:
                logger.warning(f"HLS directory not found: {hls_dir}")
    except Exception as e:
        logger.error(f"Error deleting track files: {str(e)}", exc_info=True)