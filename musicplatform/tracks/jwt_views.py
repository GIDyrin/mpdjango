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