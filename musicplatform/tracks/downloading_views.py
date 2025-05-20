from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from tracks.models import Track, Playlist
import os
import tempfile
import zipfile


class TrackDownloadView(APIView):

    def get(self, request, track_id):
        track = get_object_or_404(Track, id=track_id, user=request.user)
        
        if not track.original_file:
            return Response(
                {"error": "File not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

        response = FileResponse(track.original_file.open('rb'))
        filename = os.path.basename(track.original_file.name)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


class PlaylistDownloadView(APIView):
    
    def get(self, request, playlist_id):
        playlist = get_object_or_404(
            Playlist, 
            id=playlist_id, 
            user=request.user
        )
        tracks = playlist.tracks.all()

        if not tracks.exists():
            return Response(
                {"error": "Playlist is empty"}, 
                status=status.HTTP_404_NOT_FOUND
            )

        temp_file = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)
        try:
            with zipfile.ZipFile(temp_file, 'w') as zipf:
                for track in tracks:
                    if not track.original_file:
                        continue
                    
                    file_path = track.original_file.path
                    if not os.path.exists(file_path):
                        continue
                    
                    # Генерируем уникальное имя файла в архиве
                    arcname = f"{track.id}_{os.path.basename(file_path)}"
                    zipf.write(file_path, arcname=arcname)

            temp_file.close()

            response = FileResponse(
                open(temp_file.name, 'rb'),
                content_type='application/zip'
            )
            response['Content-Disposition'] = (
                f'attachment; filename="{playlist.name}.zip"'
            )
            return response
        finally:
            os.unlink(temp_file.name)