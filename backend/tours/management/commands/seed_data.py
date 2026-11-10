from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from tours.models import Customer, Order, Settings, Stop, Tour, Vehicle
from users.models import User

# Geslo vseh testnih uporabnikov (samo za lokalni razvoj)
SEED_PASSWORD = "turaplan123"

USERS = [
    # e-pošta, ime, priimek, vloga
    ("admin@turaplan.si", "Ana", "Admin", User.Role.ADMIN),
    ("disponent@turaplan.si", "Dejan", "Disponent", User.Role.DISPATCHER),
    ("voznik@turaplan.si", "Vid", "Voznik", User.Role.DRIVER),
    ("voznik2@turaplan.si", "Maja", "Kovač", User.Role.DRIVER),
    ("voznik3@turaplan.si", "Luka", "Horvat", User.Role.DRIVER),
]

VEHICLES = [
    # registrska, tip, nosilnost, paletna mesta
    ("MB AB-123", Vehicle.Type.VAN, 1200, 4),
    ("MB CD-456", Vehicle.Type.VAN, 1200, 4),
    ("MB TR-789", Vehicle.Type.TRUCK, 6000, 16),
]

CUSTOMERS = [
    # šifra, naziv, naslov, pošta, kraj, regija, telefon, stalna opomba
    ("C001", "Pekarna Zrno", "Glavni trg 5", "2000", "Maribor", "Štajerska", "02 123 45 67", "Zadnji vhod, zvoniti 2x"),
    ("C002", "Slaščičarna Mak", "Partizanska 12", "2000", "Maribor", "Štajerska", "02 234 56 78", ""),
    ("C003", "Pekarna Klas", "Ptujska 30", "2250", "Ptuj", "Štajerska", "02 345 67 89", ""),
    ("C004", "Gostilna Lipa", "Celjska 8", "3000", "Celje", "Savinjska", "03 456 78 90", "Dostava skozi kuhinjo"),
    ("C005", "Trgovina Sonce", "Ljubljanska 50", "3000", "Celje", "Savinjska", "03 567 89 01", ""),
    ("C006", "Pekarna Pri mlinu", "Celovška 100", "1000", "Ljubljana", "Osrednjeslovenska", "01 678 90 12", "Dostava do 7.00"),
    ("C007", "Kavarna Center", "Slovenska 20", "1000", "Ljubljana", "Osrednjeslovenska", "01 789 01 23", ""),
    ("C008", "Pekarna Bled", "Ljubljanska 4", "4260", "Bled", "Gorenjska", "04 890 12 34", ""),
    ("C009", "Bäckerei Huber", "Marienplatz 3", "80331", "München", "Nemčija – Bavarska", "+49 89 123456", "Rampa 2"),
    ("C010", "Konditorei Maier", "Hauptstraße 15", "83022", "Rosenheim", "Nemčija – Bavarska", "+49 8031 98765", ""),
]

ORDERS = [
    # številka, šifra stranke, prejeto (dni od danes), rok odpreme (dni od danes), teža kg, palete, opis
    ("N-001", "C001", -4, -1, "400", "1.5", "moka T-500 30 vreč"),
    ("N-002", "C002", -4, -1, "300", "1", "sladkor, kakav"),
    ("N-003", "C003", -3, -1, "350", "1.25", "moka, semena"),
    ("N-004", "C006", -3, 0, "300", "1", "moka T-850 20 vreč"),
    ("N-005", "C007", -2, 0, "250", "1", "kava, sladkor"),
    ("N-006", "C006", -2, 0, "200", "0.5", "kvas, sol"),
    ("N-007", "C004", -2, 0, "350", "1.25", "sir 40 kg, mleko"),
    ("N-008", "C009", -3, 1, "2000", "6", "moka T-500 120 vreč"),
    ("N-009", "C010", -3, 1, "1500", "5", "nadevi, embalaža"),
    ("N-010", "C009", -2, 1, "1200", "3.5", "semena, podstavki"),
    ("N-011", "C008", -1, 1, "500", "2", "moka, sladkor"),
    ("N-012", "C001", -1, 2, "400", "1.5", "sir 12 kg, mleko"),
    ("N-013", "C002", -5, -2, "150", "0.5", "embalaža"),
    ("N-014", "C003", -1, 1, "600", "2", "moka T-500 40 vreč"),
    ("N-015", "C004", -1, 2, "250", "0.75", "nadevi"),
    ("N-016", "C005", -1, 2, "800", "2.5", "moka, sladkor, kvas"),
    ("N-017", "C005", 0, 3, "300", "1", "podstavki"),
    ("N-018", "C006", 0, 2, "450", "1.5", "moka T-850"),
    ("N-019", "C007", 0, 3, "120", "0.25", "kava"),
    ("N-020", "C008", 0, 3, "700", "2.25", "moka, semena"),
    ("N-021", "C009", -1, 4, "1800", "5.5", "moka T-500 100 vreč"),
    ("N-022", "C010", 0, 4, "900", "3", "nadevi, sir"),
    ("N-023", "C001", 0, 4, "350", "1", "embalaža, podstavki"),
    ("N-024", "C003", 0, 5, "500", "1.75", "moka T-850 30 vreč"),
    ("N-025", "C002", 0, 5, "200", "0.5", "sladkor"),
]

TOURS = [
    # datum (dni od danes), vozilo, voznik, status, postanki: (naročilo, rezultat, razlog)
    (-1, "MB CD-456", "voznik2@turaplan.si", Tour.Status.COMPLETED, [
        ("N-001", Stop.Result.DELIVERED, ""),
        ("N-002", Stop.Result.DELIVERED, ""),
        ("N-003", Stop.Result.NOT_DELIVERED, "Stranka zaprta"),
    ]),
    (0, "MB AB-123", "voznik@turaplan.si", Tour.Status.IN_DELIVERY, [
        ("N-004", Stop.Result.DELIVERED, ""),
        ("N-006", Stop.Result.DELIVERED, ""),
        ("N-005", Stop.Result.NOT_DELIVERED, "Ni bilo nikogar"),
        ("N-007", Stop.Result.PENDING, ""),
    ]),
    (1, "MB TR-789", "voznik3@turaplan.si", Tour.Status.CONFIRMED, [
        ("N-008", Stop.Result.PENDING, ""),
        ("N-010", Stop.Result.PENDING, ""),
        ("N-009", Stop.Result.PENDING, ""),
    ]),
    (1, "MB AB-123", "voznik@turaplan.si", Tour.Status.DRAFT, [
        ("N-011", Stop.Result.PENDING, ""),
        ("N-012", Stop.Result.PENDING, ""),
    ]),
]

# Status naročila glede na rezultat postanka
ORDER_STATUS = {
    Stop.Result.PENDING: Order.Status.PLANNED,
    Stop.Result.DELIVERED: Order.Status.DELIVERED,
    Stop.Result.NOT_DELIVERED: Order.Status.NOT_DELIVERED,
}


class Command(BaseCommand):
    help = "Izbriše obstoječe ture, naročila, stranke in vozila ter naloži testne podatke"

    @transaction.atomic
    def handle(self, *args, **options):
        today = timezone.localdate()
        now = timezone.now()

        # Najprej izbrišemo stare podatke, da lahko ukaz poženemo večkrat
        Stop.objects.all().delete()
        Tour.objects.all().delete()
        Order.objects.all().delete()
        Customer.objects.all().delete()
        Vehicle.objects.all().delete()

        users = {}
        for email, first_name, last_name, role in USERS:
            user, _ = User.objects.update_or_create(
                email=email,
                defaults={"first_name": first_name, "last_name": last_name, "role": role, "is_active": True},
            )
            user.set_password(SEED_PASSWORD)
            user.save()
            users[email] = user
        dispatcher = users["disponent@turaplan.si"]

        vehicles = {
            reg: Vehicle.objects.create(registration_number=reg, type=t, max_load_kg=kg, pallet_spaces=p)
            for reg, t, kg, p in VEHICLES
        }

        customers = {}
        for code, name, address, postal, city, region, phone, note in CUSTOMERS:
            customers[code] = Customer.objects.create(
                code=code, name=name, address=address, postal_code=postal, city=city,
                region=region, phone=phone, delivery_note=note,
            )

        orders = {}
        for number, code, received, deadline, weight, pallets, description in ORDERS:
            orders[number] = Order.objects.create(
                number=number,
                customer=customers[code],
                received_date=today + timedelta(days=received),
                dispatch_deadline=today + timedelta(days=deadline),
                weight_kg=Decimal(weight),
                pallets=Decimal(pallets),
                description=description,
            )

        for days, reg, driver_email, status, stops in TOURS:
            tour = Tour.objects.create(
                dispatch_date=today + timedelta(days=days),
                vehicle=vehicles[reg],
                driver=users[driver_email],
                created_by=dispatcher,
                status=status,
            )
            # Časi prehodov glede na status ture
            if status != Tour.Status.DRAFT:
                tour.confirmed_at = now - timedelta(days=2)
            if status in (Tour.Status.IN_DELIVERY, Tour.Status.COMPLETED):
                tour.started_at = now - timedelta(hours=4)
            if status == Tour.Status.COMPLETED:
                tour.completed_at = now - timedelta(hours=1)
            tour.save()

            for sequence, (number, result, reason) in enumerate(stops, start=1):
                order = orders[number]
                Stop.objects.create(
                    tour=tour,
                    order=order,
                    sequence=sequence,
                    result=result,
                    reason=reason,
                    marked_at=None if result == Stop.Result.PENDING else now - timedelta(hours=3 - sequence * 0.5),
                )
                order.status = ORDER_STATUS[result]
                order.save()

        settings = Settings.load()
        settings.warehouse_address = "Industrijska ulica 10, 2000 Maribor"
        settings.save()

        self.stdout.write(self.style.SUCCESS(
            f"Naloženo: {len(USERS)} uporabnikov, {len(VEHICLES)} vozila, {len(CUSTOMERS)} strank, "
            f"{len(ORDERS)} naročil, {len(TOURS)} ture. Geslo uporabnikov: {SEED_PASSWORD}"
        ))
