from celery import shared_task
import subprocess
import os
from django.conf import settings
from .models import Track

@shared_task
def convert_to_hls(track_id):
    track = Track.objects.get(id=track_id)
    
    # Пути
    input_path = track.original_file.path
    output_dir = os.path.join(settings.MEDIA_ROOT, f"hls/{track_id}")
    os.makedirs(output_dir, exist_ok=True)
    
    # Команда FFmpeg
    cmd = f"""
    ffmpeg -i {input_path} \
    -codec: copy \
    -start_number 0 \
    -hls_time 10 \
    -hls_list_size 0 \
    -f hls {output_dir}/playlist.m3u8
    """
    
    # Запуск
    try:
        subprocess.run(cmd, shell=True, check=True)
        track.hls_playlist = f"hls/{track_id}/playlist.m3u8"
        track.save()
    except Exception as e:
        track.delete()
        raise e