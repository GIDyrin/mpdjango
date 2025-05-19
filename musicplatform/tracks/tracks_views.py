from rest_framework import generics, status, views
from rest_framework.response import Response
from .models import Track, Playlist
from .serializers import TrackUploadSerializer
import shutil
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from tempfile import NamedTemporaryFile
from django.conf import settings
from rest_framework.parsers import MultiPartParser, FormParser
from .tasks import convert_to_hls
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

import logging

logger = logging.getLogger(__name__)

class TrackUploadView(generics.CreateAPIView):
    serializer_class = TrackUploadSerializer
    parser_classes = [MultiPartParser, FormParser]

    def handle_chunk(self, request):
        chunk = request.FILES['chunk']
        file_id = request.POST['file_id']
        chunk_index = int(request.POST['chunk_index'])
        total_chunks = int(request.POST['total_chunks'])
        
        # Сохраняем чанк во временную директорию
        tmp_dir = os.path.join(settings.MEDIA_ROOT, 'tmp', file_id)
        os.makedirs(tmp_dir, exist_ok=True)
        
        chunk_name = os.path.join(tmp_dir, f'chunk_{chunk_index:04d}')
        with default_storage.open(chunk_name, 'wb') as f:
            for chunk_part in chunk.chunks():
                f.write(chunk_part)
        
        # Проверяем завершение загрузки
        if chunk_index + 1 == total_chunks:
            return self.finalize_upload(request, file_id, tmp_dir)
        
        return Response({'status': 'chunk_uploaded'})

    def finalize_upload(self, request, file_id, tmp_dir):
        # Собираем файл из чанков
        original_filename = request.POST['original_filename']
        final_filename = default_storage.get_available_name(
            os.path.join('tracks/original', original_filename)
        )
        
        with NamedTemporaryFile('wb', delete=False) as final_file:
            for chunk_name in sorted(os.listdir(tmp_dir)):
                chunk_path = os.path.join(tmp_dir, chunk_name)
                with open(chunk_path, 'rb') as chunk_file:
                    final_file.write(chunk_file.read())
                os.remove(chunk_path)
            os.rmdir(tmp_dir)
            final_file.flush()
        
        # Сохраняем трек в БД
        track_data = {
            'user': request.user.id,
            'title': request.POST['title'],
            'artist': request.POST['artist'],
            'duration': request.POST['duration'],
            'original_file': ContentFile(
                open(final_file.name, 'rb').read(),
                name=final_filename
            )
        }
        
        serializer = self.get_serializer(data=track_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Добавляем в системный плейлист
        system_playlist, _ = Playlist.objects.get_or_create(
            user=request.user,
            is_system=True,
            defaults={'name': 'System Playlist'}
        )
        system_playlist.tracks.add(serializer.instance)
        system_playlist.save()
        
        # Запускаем конвертацию
        convert_to_hls.delay(serializer.instance.id)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def create(self, request, *args, **kwargs):
        try:
            if 'chunk' in request.FILES:
                return self.handle_chunk(request)
            # Старая реализация для обратной совместимости
            return super().create(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Upload error: {str(e)}", exc_info=True)
            return Response(
                {"error": "File upload failed"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PlaylistTrackDeleteView(views.APIView):
    
    def delete(self, request, playlist_id, track_id):
        try:
            playlist = Playlist.objects.get(id=playlist_id, user=request.user)
            track = Track.objects.get(id=track_id, user=request.user)
        except (Playlist.DoesNotExist, Track.DoesNotExist):
            return Response(status=status.HTTP_404_NOT_FOUND)

        if playlist.is_system:
            # Полное удаление трека
            file_path = track.original_file.path
            hls_dir = os.path.join(
                settings.MEDIA_ROOT, 
                os.path.dirname(track.hls_playlist)
            )

            if os.path.exists(file_path):
                os.remove(file_path)
            
            if os.path.exists(hls_dir):
                shutil.rmtree(hls_dir)
            
            track.delete()
        else:
            # Удаление из плейлиста
            playlist.tracks.remove(track)

        return Response(status=status.HTTP_204_NO_CONTENT)
    


class TrackHLSView(views.APIView):
    def get(self, request, track_id):
        try:
            track = Track.objects.get(id=track_id)
        except Track.DoesNotExist:
            return Response(
                {'error': 'Track not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        if not track.hls_playlist:
            return Response(
                {'error': 'HLS is not ready for this track'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        hls_url = request.build_absolute_uri(f'/media/hls/{track.hls_playlist}')
        return Response({
            'hls_url': hls_url,
            'mime_type': 'application/vnd.apple.mpegurl',
            'content_type': 'audio'
        }, status=status.HTTP_200_OK)