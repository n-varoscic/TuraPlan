from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Ustvarjanje uporabnikov s prijavo z e-pošto namesto uporabniškega imena"""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("E-pošta je obvezna")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        # Ukaz createsuperuser ustvari administratorja
        extra_fields["role"] = User.Role.ADMIN
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Uporabnik aplikacije z eno od treh vlog"""

    class Role(models.TextChoices):
        DISPATCHER = "DISPATCHER", "Disponent"
        DRIVER = "DRIVER", "Voznik"
        ADMIN = "ADMIN", "Administrator"

    # Prijava z e-pošto, zato uporabniškega imena ne potrebujemo
    username = None
    email = models.EmailField("e-pošta", unique=True)
    phone = models.CharField("telefon", max_length=30, blank=True)
    role = models.CharField("vloga", max_length=20, choices=Role.choices)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "uporabnik"
        verbose_name_plural = "uporabniki"

    def save(self, *args, **kwargs):
        # Samo administrator ima dostop do Django Admina
        self.is_staff = self.is_superuser = self.role == self.Role.ADMIN
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})".strip()
