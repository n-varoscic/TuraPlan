from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import LoginSerializer, UserSerializer


class LoginView(TokenObtainPairView):
    """POST /api/auth/login/ z e-pošto in geslom"""

    serializer_class = LoginSerializer


class MeView(APIView):
    """GET /api/auth/me/ vrne prijavljenega uporabnika in njegovo vlogo"""

    def get(self, request):
        return Response(UserSerializer(request.user).data)
