from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from django.core.cache import cache

class JWTBlacklistMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            try:
                # Декодируем токен
                auth = JWTTokenUserAuthentication()
                validated_token = auth.get_validated_token(auth_header.split(' ')[1])
                jti = validated_token.get('jti')

                # Проверяем чёрный список
                if cache.get(f'blacklist_{jti}'):
                    return JsonResponse({'error': 'TOKEN REVOKED'}, status=401)
            except:
                return JsonResponse({'error': 'INVALID TOKEN'}, status=401)

        return self.get_response(request)