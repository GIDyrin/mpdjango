from rest_framework import generics, status
from rest_framework.response import Response
from .models import Track, Playlist
from .serializers import TrackSerializer, TrackUploadSerializer
import shutil
import os
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

    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                user = request.user
                tracks_data = []
                
                # Определяем количество треков
                num_tracks = sum(
                    1 for key in request.FILES 
                    if key.startswith('tracks[') and key.endswith('].original_file')
                )

                for i in range(num_tracks):
                    file_key = f'tracks[{i}].original_file'
                    track_data = {
                        'original_file': request.FILES[file_key],
                        'title': request.data.get(f'tracks[{i}].title', 'Untitled'),
                        'artist': request.data.get(f'tracks[{i}].artist', 'Unknown Artist'),
                        'duration': request.data.get(f'tracks[{i}].duration', 0),
                        'user': user.id
                    }
                    tracks_data.append(track_data)

                serializer = self.get_serializer(data=tracks_data, many=True)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                
                try:
                    system_playlist = Playlist.objects.get(user=user, is_system=True)
                except ObjectDoesNotExist:
                    system_playlist = Playlist.objects.create(
                        user=user,
                        name="System Playlist",
                        is_system=True
                    )

                system_playlist.tracks.add(*serializer.instance)
                system_playlist.save()

                # Запуск задач конвертации
                for track in serializer.instance:
                    convert_to_hls.delay(track.id)

                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Upload error: {str(e)}", exc_info=True)
            return Response(
                {"error": "File upload failed"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TrackDeleteView(generics.DestroyAPIView):
    queryset = Track.objects.all()
    
    def get_queryset(self):
        return Track.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        # Удаляем файлы и директории
        file_path = instance.original_file.path
        hls_dir = os.path.join(settings.MEDIA_ROOT, os.path.dirname(instance.hls_playlist))
        
        # Удаляем оригинальный файл
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Удаляем HLS-директорию
        if os.path.exists(hls_dir):
            shutil.rmtree(hls_dir)
        
        # Удаляем запись из БД
        instance.delete()