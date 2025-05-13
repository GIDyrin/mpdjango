from rest_framework import generics, status
from rest_framework.response import Response
from .models import Track
from .serializers import TrackSerializer
import shutil
import os
from django.conf import settings
from rest_framework.parsers import MultiPartParser
from .tasks import convert_to_hls


class TrackUploadView(generics.CreateAPIView):
    serializer_class = TrackSerializer
    parser_classes = [MultiPartParser]
    
    def post(self, request, *args, **kwargs):
        # Поддержка нескольких файлов
        files = request.FILES.getlist('original_file')
        tracks = []
        
        for file in files:
            serializer = self.get_serializer(data={
                'user': request.user.id,
                'original_file': file,
                'title': request.data.get('title', file.name),
                'artist': request.data.get('artist', 'Unknown Artist')
            })
            serializer.is_valid(raise_exception=True)
            track = serializer.save()
            tracks.append(track)
            
            # Запуск задачи конвертации
            convert_to_hls.delay(track.id)
        
        return Response(
            {"status": f"{len(tracks)} tracks uploaded"}, 
            status=status.HTTP_201_CREATED
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