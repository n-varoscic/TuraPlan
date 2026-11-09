from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import BaseUserCreationForm, UserChangeForm

from .models import User


# Vgrajena obrazca sta narejena za uporabniško ime, naš uporabnik pa se prijavi z e-pošto
class UserCreateForm(BaseUserCreationForm):
    class Meta:
        model = User
        fields = ["email"]


class UserEditForm(UserChangeForm):
    class Meta:
        model = User
        fields = "__all__"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Urejanje uporabnikov v Django Admin (prijava z e-pošto, brez uporabniškega imena)"""

    add_form = UserCreateForm
    form = UserEditForm
    list_display = ["email", "first_name", "last_name", "role", "is_active"]
    list_filter = ["role", "is_active"]
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["email"]

    # Polja na strani za urejanje obstoječega uporabnika
    fieldsets = [
        (None, {"fields": ["email", "password"]}),
        ("Osebni podatki", {"fields": ["first_name", "last_name", "phone"]}),
        ("Dostop", {"fields": ["role", "is_active"]}),
        ("Časi", {"fields": ["last_login", "date_joined"]}),
    ]
    # Polja na strani za dodajanje novega uporabnika
    add_fieldsets = [
        (None, {"fields": ["email", "password1", "password2"]}),
        ("Osebni podatki", {"fields": ["first_name", "last_name", "phone"]}),
        ("Dostop", {"fields": ["role", "is_active"]}),
    ]
