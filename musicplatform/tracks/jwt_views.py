from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .models import Track
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework import status
from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken, 
    BlacklistedToken
)
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    authentication_classes = [] 
    permission_classes = [AllowAny]


class CustomTokenRefreshView(TokenRefreshView):
    pass
            

class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            return Response(
                {'message': 'Successfully logged out'}, 
                status=status.HTTP_205_RESET_CONTENT
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        


import logging
logger = logging.getLogger(__name__)
from django.db import transaction

class AccountDeleteView(APIView):

    def post(self, request):
        try:
            with transaction.atomic():
                logger.info(f"Starting account deletion for user {request.user.id}")
                
                password = request.data.get('password')
                if not password:
                    logger.warning("Password not provided")
                    return Response(...)

                if not request.user.check_password(password):
                    logger.warning("Invalid password provided")
                    return Response(...)

                user = request.user
                logger.info(f"Processing deletion for {user.username}")

                # Явное удаление треков
                tracks = Track.objects.filter(user=user)
                logger.info(f"Found {tracks.count()} tracks to delete")
                
                for track in tracks:
                    logger.debug(f"Deleting track {track.id}")
                    track.delete()

                # Удаление пользователя
                logger.info("Deleting user account")
                user.delete()

                return Response(
                {'message': 'Account and all associated tracks deleted'},
                status=status.HTTP_204_NO_CONTENT
                )

        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )