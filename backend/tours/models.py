from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator, MinValueValidator
from django.db import models

from users.models import User


def validate_quarter(value):
    """Palete morajo biti podane na 0,25 natančno"""
    if value % Decimal("0.25") != 0:
        raise ValidationError("Število palet mora biti deljivo z 0,25")


class Customer(models.Model):
    """Stranka, ki ji dostavljamo (podatki prihajajo iz ERP)"""

    code = models.CharField("šifra", max_length=20, unique=True)
    name = models.CharField("naziv", max_length=200)
    address = models.CharField("naslov", max_length=200)
    postal_code = models.CharField("pošta", max_length=10)
    city = models.CharField("kraj", max_length=100)
    region = models.CharField("regija", max_length=100)
    lat = models.DecimalField("zemljepisna širina", max_digits=9, decimal_places=6, null=True, blank=True)
    lng = models.DecimalField("zemljepisna dolžina", max_digits=9, decimal_places=6, null=True, blank=True)
    # Naslov, za katerega veljata lat in lng; če se naslov stranke spremeni, koordinate poiščemo znova
    geocoded_address = models.CharField("naslov koordinat", max_length=320, blank=True)
    contact_name = models.CharField("kontaktna oseba", max_length=100, blank=True)
    phone = models.CharField("telefon", max_length=30, blank=True)
    delivery_note = models.CharField("stalna opomba za dostavo", max_length=300, blank=True)
    is_active = models.BooleanField("aktivna", default=True)

    class Meta:
        verbose_name = "stranka"
        verbose_name_plural = "stranke"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Vehicle(models.Model):
    """Kombi ali tovornjak z nosilnostjo in številom paletnih mest"""

    class Type(models.TextChoices):
        VAN = "VAN", "Kombi"
        TRUCK = "TRUCK", "Tovornjak"

    registration_number = models.CharField("registrska številka", max_length=20, unique=True)
    type = models.CharField("tip", max_length=10, choices=Type.choices)
    max_load_kg = models.PositiveIntegerField("nosilnost (kg)", validators=[MinValueValidator(1)])
    pallet_spaces = models.PositiveIntegerField("paletna mesta", validators=[MinValueValidator(1)])
    is_active = models.BooleanField("aktivno", default=True)

    class Meta:
        verbose_name = "vozilo"
        verbose_name_plural = "vozila"
        ordering = ["registration_number"]

    def __str__(self):
        return f"{self.registration_number} ({self.get_type_display()})"


class Order(models.Model):
    """Naročilo ene stranke s težo in številom palet"""

    class Status(models.TextChoices):
        NEW = "NEW", "Novo"
        PLANNED = "PLANNED", "Planirano"
        DELIVERED = "DELIVERED", "Dostavljeno"
        NOT_DELIVERED = "NOT_DELIVERED", "Nedostavljeno"

    number = models.CharField("številka", max_length=20, unique=True)
    customer = models.ForeignKey(
        Customer, verbose_name="stranka", on_delete=models.PROTECT, related_name="orders"
    )
    received_date = models.DateField("datum prejema")
    dispatch_deadline = models.DateField("rok odpreme")
    weight_kg = models.DecimalField(
        "teža (kg)", max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    pallets = models.DecimalField(
        "palete",
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.25")), validate_quarter],
    )
    description = models.CharField("opis", max_length=300, blank=True)
    status = models.CharField("status", max_length=20, choices=Status.choices, default=Status.NEW)

    class Meta:
        verbose_name = "naročilo"
        verbose_name_plural = "naročila"
        ordering = ["dispatch_deadline", "number"]

    def __str__(self):
        return f"{self.number} – {self.customer}"


class Tour(models.Model):
    """Ena vožnja enega vozila z enim voznikom na datum odpreme"""

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Osnutek"
        CONFIRMED = "CONFIRMED", "Potrjena"
        IN_DELIVERY = "IN_DELIVERY", "V dostavi"
        COMPLETED = "COMPLETED", "Zaključena"

    dispatch_date = models.DateField("datum odpreme")
    vehicle = models.ForeignKey(
        Vehicle, verbose_name="vozilo", on_delete=models.PROTECT, related_name="tours"
    )
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="voznik",
        on_delete=models.PROTECT,
        related_name="driven_tours",
        limit_choices_to={"role": User.Role.DRIVER},
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="ustvaril",
        on_delete=models.PROTECT,
        related_name="created_tours",
        limit_choices_to={"role": User.Role.DISPATCHER},
    )
    status = models.CharField("status", max_length=20, choices=Status.choices, default=Status.DRAFT)
    note = models.CharField("opomba", max_length=300, blank=True)
    confirmed_at = models.DateTimeField("potrjeno ob", null=True, blank=True)
    started_at = models.DateTimeField("začetek ob", null=True, blank=True)
    completed_at = models.DateTimeField("zaključeno ob", null=True, blank=True)

    class Meta:
        verbose_name = "tura"
        verbose_name_plural = "ture"
        ordering = ["dispatch_date", "id"]
        constraints = [
            # Vozilo in voznik imata na isti datum odpreme največ eno turo
            models.UniqueConstraint(
                fields=["dispatch_date", "vehicle"], name="unique_vehicle_per_date",
                violation_error_message="Vozilo ima na ta datum že turo",
            ),
            models.UniqueConstraint(
                fields=["dispatch_date", "driver"], name="unique_driver_per_date",
                violation_error_message="Voznik ima na ta datum že turo",
            ),
        ]

    def __str__(self):
        return f"Tura {self.dispatch_date:%d. %m. %Y} – {self.vehicle.registration_number}"


class Stop(models.Model):
    """Eno naročilo v turi z zaporedno številko in rezultatom dostave"""

    class Result(models.TextChoices):
        PENDING = "PENDING", "Čaka"
        DELIVERED = "DELIVERED", "Dostavljeno"
        NOT_DELIVERED = "NOT_DELIVERED", "Ni dostavljeno"

    tour = models.ForeignKey(Tour, verbose_name="tura", on_delete=models.CASCADE, related_name="stops")
    order = models.ForeignKey(Order, verbose_name="naročilo", on_delete=models.PROTECT, related_name="stops")
    sequence = models.PositiveIntegerField("zaporedje", validators=[MinValueValidator(1)])
    driver_note = models.CharField(
        "opomba za voznika", max_length=300, blank=True, validators=[MaxLengthValidator(300)]
    )
    result = models.CharField("rezultat", max_length=20, choices=Result.choices, default=Result.PENDING)
    reason = models.CharField("razlog nedostave", max_length=300, blank=True)
    marked_at = models.DateTimeField("označeno ob", null=True, blank=True)

    class Meta:
        verbose_name = "postanek"
        verbose_name_plural = "postanki"
        ordering = ["tour", "sequence"]
        constraints = [
            models.UniqueConstraint(
                fields=["tour", "sequence"], name="unique_sequence_per_tour",
                violation_error_message="Zaporedna številka v turi že obstaja",
            ),
        ]

    def __str__(self):
        return f"{self.sequence}. {self.order}"


class Settings(models.Model):
    """Sistemske nastavitve, v tabeli je vedno samo ena vrstica (id = 1)"""

    warehouse_address = models.CharField("naslov skladišča", max_length=200)
    warehouse_lat = models.DecimalField("širina skladišča", max_digits=9, decimal_places=6, null=True, blank=True)
    warehouse_lng = models.DecimalField("dolžina skladišča", max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        verbose_name = "nastavitve"
        verbose_name_plural = "nastavitve"

    def save(self, *args, **kwargs):
        # Vedno shranimo v isto vrstico, zato druge vrstice ni mogoče ustvariti
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        """Vrne edino vrstico nastavitev (ustvari jo, če še ne obstaja)"""
        obj, _ = cls.objects.get_or_create(pk=1, defaults={"warehouse_address": ""})
        return obj

    def __str__(self):
        return "Nastavitve"
