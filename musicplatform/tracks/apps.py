from django.apps import AppConfig
from django.db.models.signals import post_save, pre_delete



class TracksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tracks'

    def ready(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Импортируем обработчик сигнала
        from .signals import create_system_playlist, delete_track_files
        from tracks.models import Track
        
        # Регистрируем сигнал
        post_save.connect(create_system_playlist, sender=User)
        pre_delete.connect(delete_track_files, sender=Track)


