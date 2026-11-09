from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User


class LoginSerializer(TokenObtainPairSerializer):
    """Prijava z e-pošto in geslom, vrne dostopni žeton in žeton za osvežitev"""

    # Enako sporočilo za napačno e-pošto, napačno geslo in deaktiviranega uporabnika
    default_error_messages = {"no_active_account": "Napačna e-pošta ali geslo"}


class UserSerializer(serializers.ModelSerializer):
    """Podatki o uporabniku, ki jih potrebuje frontend"""

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "phone", "role"]
