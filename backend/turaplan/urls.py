"""
Glavna URL konfiguracija: poveže naslove (URL) s pogledi (views)

- Končne točke API se začnejo z /api/
- Django Admin je na /admin/
"""

from django.contrib import admin
from django.urls import path

from .views import health

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health, name="health"),
]
