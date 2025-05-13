from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserRegistrationSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import AllowAny

class UserRegistrationView(APIView):
    authentication_classes = []  # Отключаем аутентификацию
    permission_classes = [AllowAny]  # Разрешаем доступ всем


    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Пользователь создан"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserInfoView(APIView):

    def get(self, request):
        return Response({
            'username': request.user.username,
            'email': request.user.email
        })