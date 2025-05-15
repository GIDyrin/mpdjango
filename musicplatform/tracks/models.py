from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Track(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255, blank=True, default="Unknown Artist")
    duration = models.PositiveIntegerField(help_text="Duration in seconds", default=120)  # Новое поле
    original_file = models.FileField(upload_to='tracks/original/')
    hls_playlist = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.artist}"


class Playlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    tracks = models.ManyToManyField(Track)
    is_system = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"


    def delete(self, *args, **kwargs):
        if self.is_system:
            raise ValueError("System playlist cannot be deleted.")
        super().delete(*args, **kwargs)