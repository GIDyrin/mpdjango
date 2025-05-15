import os
import subprocess
import shutil
import logging
from celery import shared_task
from django.conf import settings
from tracks.models import Track  # Замените на ваш фактический импорт модели Track

logger = logging.getLogger(__name__)

@shared_task
def convert_to_hls(track_id):
    track = None  # Инициализируем переменную track, чтобы избежать ошибки в случае исключения
    try:
        track = Track.objects.get(id=track_id)
        input_path = track.original_file.path
        output_dir = os.path.join(settings.MEDIA_ROOT, f"hls/{track_id}")
        
        # Создаем выходную директорию, если она не существует
        os.makedirs(output_dir, exist_ok=True)
        
        # Формируем команду для ffmpeg
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-map', '0:a',  # Выбираем только аудиодорожку
            '-c:a', 'aac',  # Кодек AAC
            '-b:a', '128k', # Битрейт 128 kbps (128 чтобы гарантированно преобразовать)
            '-f', 'hls',
            '-hls_time', '10',  # Длина сегмента 10 секунд
            '-hls_list_size', '0',  
            '-hls_segment_filename', f'{output_dir}/segment_%03d.ts',  # Формат имен для сегментов
            f'{output_dir}/playlist.m3u8' 
        ]

        # Запускаем ffmpeg
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Проверка результата
        if not os.path.exists(f'{output_dir}/playlist.m3u8'):
            raise Exception("HLS playlist not created")
            
        # Сохраняем путь к плейлисту в базе данных
        track.hls_playlist = f"hls/{track_id}/playlist.m3u8"
        track.save()
        
    except Exception as e:
        logger.error(f"Conversion failed for track {track_id}: {str(e)}")
        if track:
            track.delete()  # Удаляем трек в случае ошибки
        shutil.rmtree(output_dir, ignore_errors=True)  # Удаляем выходную директорию, если она существует
        raise
