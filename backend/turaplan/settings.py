"""
Nastavitve Django projekta TuraPlan

- Osnovo je ustvaril ukaz `django-admin startproject` (Django 5.2)
- Vrednosti, ki se razlikujejo med okolji (skrivni ključ, DEBUG, pot do baze),
  se preberejo iz okoljskih spremenljivk, sicer veljajo privzete za lokalni razvoj
"""

import os
from datetime import timedelta
from pathlib import Path

# Mapa backend/, od katere se računajo vse poti v projektu
BASE_DIR = Path(__file__).resolve().parent.parent


# Varnost
# Privzeti ključ je samo za lokalni razvoj, v produkciji se nastavi DJANGO_SECRET_KEY
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-samo-za-lokalni-razvoj-zamenjaj-v-produkciji",
)

DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")


# Aplikacije
INSTALLED_APPS = [
    # Vgrajene Django aplikacije
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Zunanje knjižnice
    "rest_framework",  # Django REST Framework za REST API v JSON
    "corsheaders",  # Dovoli zahteve s frontenda na drugem naslovu (CORS)
    # Naše aplikacije
    "users",
]

MIDDLEWARE = [
    # CorsMiddleware mora biti čim višje, da doda CORS glave vsem odgovorom
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "turaplan.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "turaplan.wsgi.application"


# Podatkovna baza – SQLite (ADR-05)
# Pot do baze se lahko nastavi z DJANGO_DB_PATH (Docker, da baza ostane ohranjena)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.environ.get("DJANGO_DB_PATH", BASE_DIR / "db.sqlite3"),
    }
}


# Lasten model uporabnika s prijavo z e-pošto in vlogo
AUTH_USER_MODEL = "users.User"


# Preverjanje gesel
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Jezik in čas
LANGUAGE_CODE = "sl"
TIME_ZONE = "Europe/Ljubljana"
USE_I18N = True
USE_TZ = True


# Statične datoteke (CSS in JS za Django Admin)
STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# CORS: naslovi frontenda, s katerih backend sprejema zahteve
# Vite razvojni strežnik privzeto teče na http://localhost:5173
CORS_ALLOWED_ORIGINS = os.environ.get(
    "DJANGO_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
).split(",")


# Django REST Framework: vsak API privzeto zahteva prijavo z JWT žetonom
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

# JWT: kratkotrajni dostopni žeton in dolgotrajnejši žeton za osvežitev
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}
