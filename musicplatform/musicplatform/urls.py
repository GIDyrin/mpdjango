"""
URL configuration for musicplatform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from tracks.jwt_views import *
from tracks.views import *


urlpatterns = [
    #WITHOUT JWT
    path('admin/', admin.site.urls),
    path('api/auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain'),
    path('api/auth/register/', UserRegistrationView.as_view(), name='register'),

    #Защищенные пути
    path('api/auth/me/', UserInfoView.as_view(), name='user_me'),
    path('api/auth/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/logout/', LogoutView.as_view(), name='tokens_revoking'),
    path('api/me/playlists/', PlaylistListCreateView.as_view(), name='playlist-list'),
    path('api/playlists/<int:pk>/', PlaylistDetailView.as_view(), name='playlist-detail'),
    path('api/playlists/<int:pk>/add-tracks/', PlaylistAddTracksView.as_view(), name='playlist-add-tracks'),
    path('api/tracks/upload/', TrackUploadView.as_view(), name='track-upload'),
    path('api/playlists/<int:playlist_id>/tracks/<int:track_id>/', PlaylistTrackDeleteView.as_view(), name='playlist-remove-track'),
    path('api/playlists/system/', SystemPlaylistView.as_view(), name='get_system_playlist'),
    path('api/tracks/<int:track_id>/hls/', TrackHLSView.as_view(), name='track-hls'),
    path('api/tracks/<int:track_id>/download/', TrackDownloadView.as_view(), name='track-download'),
    path('api/playlists/<int:playlist_id>/download/', PlaylistDownloadView.as_view(), name='playlist-download'),
    path('api/auth/delete-account/', AccountDeleteView.as_view(), name='delete_account')
]
