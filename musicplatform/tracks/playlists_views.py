from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Track, Playlist
from .serializers import PlaylistSerializer, PlaylistDetailedSerializer


class PlaylistListCreateView(generics.ListCreateAPIView):
    serializer_class = PlaylistSerializer

    def get_queryset(self):
        return Playlist.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            is_system=False  # Явно устанавливаем для новых плейлистов
        )


class PlaylistDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = PlaylistDetailedSerializer

    def get_queryset(self):
        return Playlist.objects.filter(user=self.request.user)


class PlaylistAddTracksView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        playlist = generics.get_object_or_404(Playlist, pk=pk, user=request.user)
        track_ids = request.data.get('track_ids', [])
        
        # Проверка прав на треки
        tracks = Track.objects.filter(
            id__in=track_ids,
            user=request.user
        )
        
        playlist.tracks.add(*tracks)
        return Response({"status": "tracks added"}, status=status.HTTP_200_OK)

