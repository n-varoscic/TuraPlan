from datetime import date
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import IntegrityError

from tours.models import Customer, Order, Settings, Tour, Vehicle
from users.models import User


@pytest.fixture
def customer(db):
    return Customer.objects.create(
        code="C1", name="Pekarna", address="Ulica 1", postal_code="2000", city="Maribor", region="Štajerska"
    )


def make_order(customer, pallets):
    return Order(
        number="N1", customer=customer, received_date=date(2026, 11, 1),
        dispatch_deadline=date(2026, 11, 3), weight_kg=Decimal("100"), pallets=Decimal(pallets),
    )


@pytest.mark.parametrize("pallets", ["0.25", "1", "2.75"])
def test_pallets_in_quarters_are_valid(customer, pallets):
    make_order(customer, pallets).full_clean()


@pytest.mark.parametrize("pallets", ["0.3", "1.1", "0"])
def test_pallets_not_in_quarters_are_invalid(customer, pallets):
    with pytest.raises(ValidationError):
        make_order(customer, pallets).full_clean()


def test_vehicle_can_have_only_one_tour_per_date(db):
    vehicle = Vehicle.objects.create(registration_number="MB 1", type="VAN", max_load_kg=1200, pallet_spaces=4)
    dispatcher = User.objects.create_user("d@t.si", "x", role=User.Role.DISPATCHER)
    driver1 = User.objects.create_user("v1@t.si", "x", role=User.Role.DRIVER)
    driver2 = User.objects.create_user("v2@t.si", "x", role=User.Role.DRIVER)
    day = date(2026, 11, 10)
    Tour.objects.create(dispatch_date=day, vehicle=vehicle, driver=driver1, created_by=dispatcher)
    with pytest.raises(IntegrityError):
        Tour.objects.create(dispatch_date=day, vehicle=vehicle, driver=driver2, created_by=dispatcher)


def test_settings_always_has_one_row(db):
    Settings(warehouse_address="A").save()
    Settings(warehouse_address="B").save()
    assert Settings.objects.count() == 1
    assert Settings.load().warehouse_address == "B"


def test_seed_data_can_run_twice(db):
    call_command("seed_data")
    call_command("seed_data")
    assert Order.objects.count() == 100
    assert Tour.objects.count() == 4
