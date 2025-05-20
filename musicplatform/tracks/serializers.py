from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Track, Playlist
from django.db.models import Case, When

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = '__all__'
        extra_kwargs = {
            'original_file': {'required': True, 'allow_empty_file': False}
        }


class TrackUploadSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    
    class Meta:
        model = Track
        fields = '__all__'
        read_only_fields = ('hls_playlist', 'created_at')
        extra_kwargs = {
            'original_file': {'required': True, 'allow_empty_file': False}
        }

        
class PlaylistSerializer(serializers.ModelSerializer):
    track_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Playlist
        fields = ['id', 'name', 'track_count', 'is_system', 'created_at']
        read_only_fields = ['is_system']
        extra_kwargs = {
            'name': {'required': True}
        }
    
    def get_track_count(self, obj):
        return obj.tracks.count()
    

class PlaylistDetailedSerializer(serializers.ModelSerializer):
    tracks = serializers.SerializerMethodField()
    
    class Meta:
        model = Playlist
        fields = '__all__'
    
    def get_tracks(self, obj):
        if obj.is_system:
            return TrackSerializer(
                obj.tracks.all().order_by('created_at'),
                many=True,
                context=self.context
            ).data
        else:
            # Получаем правильный порядок треков через промежуточную модель
            ordered_tracks = obj.tracks.through.objects.filter(playlist=obj)\
                .order_by('id')\
                .values_list('track', flat=True)
            
            # Сохраняем порядок с помощью сохранения порядка ID
            preserved_order = Case(
                *[When(pk=pk, then=pos) for pos, pk in enumerate(ordered_tracks)])
            
            return TrackSerializer(
                obj.tracks.filter(id__in=ordered_tracks)\
                    .order_by(preserved_order),
                many=True,
                context=self.context
            ).data