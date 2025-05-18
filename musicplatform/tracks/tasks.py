import os
import subprocess
import shutil
import logging
from celery import shared_task
from django.conf import settings
from tracks.models import Track  # Замените на ваш фактический импорт модели Track

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def convert_to_hls(self, track_id):
    track = Track.objects.get(id=track_id)
    input_path = track.original_file.path
    output_dir = os.path.join(settings.MEDIA_ROOT, f"hls/{track_id}")
    
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        # Проверка битрейта исходного файла
        probe_cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'a:0',
            '-show_entries', 'stream=bit_rate',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            input_path
        ]
        bitrate = subprocess.check_output(probe_cmd, text=True).strip()
        target_bitrate = min(int(bitrate) if bitrate.isdigit() else 128000, 128000)

        cmd = [
            'ffmpeg',
            '-y',
            '-i', input_path,
            '-map', '0:a',
            '-c:a', 'aac',
            '-b:a', f'{target_bitrate // 1000}k',
            '-f', 'hls',
            '-hls_time', '10',
            '-hls_playlist_type', 'event',  # Изменено с vod на event
            '-hls_segment_filename', f'{output_dir}/segment_%03d.ts',
            f'{output_dir}/playlist.m3u8'
        ]

        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        track.hls_playlist = f"{track_id}/playlist.m3u8"
        track.save()
        
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg error: {e.output}")
        shutil.rmtree(output_dir, ignore_errors=True)
        self.retry(countdown=60 * (self.request.retries + 1))
    except Exception as e:
        logger.error(f"Conversion error: {str(e)}")
        shutil.rmtree(output_dir, ignore_errors=True)
        track.hls_playlist = ""
        track.save()