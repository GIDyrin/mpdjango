from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.core.cache import cache
from rest_framework.permissions import AllowAny

class CustomTokenObtainPairView(TokenObtainPairView):
    authentication_classes = [] 
    permission_classes = [AllowAny]


#REFRESHING TOKEN /api/token/refresh
class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        # Получаем старый Access Token из запроса
        old_access_token = request.auth
        if old_access_token:
            # Добавляем его в чёрный список
            jti = old_access_token.get('jti')
            cache.set(f'blacklist_{jti}', 'revoked', timeout=old_access_token.lifetime.total_seconds())

        # Вызов базового конструктора для эндпоинта
        response = super().post(request, *args, **kwargs)
        return response
    

#Logout
class LogoutView(APIView):
    def post(self, request):
        # Блокируем Access Token
        try:
            access_token = request.auth 
            access_jti = AccessToken(access_token).get('jti')
            cache.set(f'blacklist_{access_jti}', 'revoked', timeout=access_token.lifetime.total_seconds())
        except:
            pass

        # Блокируем Refresh Token
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        refresh_jti = token.get('jti')
        cache.set(f'blacklist_{refresh_jti}', 'revoked', timeout=token.lifetime.total_seconds())

        return Response({'message': 'Logged out'})