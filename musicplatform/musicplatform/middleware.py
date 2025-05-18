from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken



class JWTBlacklistMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            auth = JWTAuthentication().authenticate(request)
            if auth:
                token = auth[1]
                jti = token.payload.get('jti')
                if BlacklistedToken.objects.filter(token__jti=jti).exists():
                    raise InvalidToken('Token is blacklisted')
        except Exception:
            pass

        return self.get_response(request)