from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework import status
from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken, 
    BlacklistedToken
)

class CustomTokenObtainPairView(TokenObtainPairView):
    authentication_classes = [] 
    permission_classes = [AllowAny]


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get('refresh')
        
        try:
            # Добавляем старый refresh-токен в черный список
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            # Генерируем новые токены
            response = super().post(request, *args, **kwargs)
            
            return response
            
        except TokenError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
    

class LogoutView(APIView):

    def post(self, request):
        try:
            # Добавляем access token в черный список
            access_token = request.auth
            jti = access_token.get('jti')
            token = OutstandingToken.objects.get(jti=jti)
            BlacklistedToken.objects.get_or_create(token=token)

            # Добавляем refresh token в черный список
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