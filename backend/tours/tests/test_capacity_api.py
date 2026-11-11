from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from tours.management.commands.seed_data import DISPATCHER_EMAIL, DRIVER_MAJA_EMAIL
from tours.models import Customer, Order, Tour, Vehicle
from tours.services import add_stop
from users.models import User


@pytest.fixture
def tomorrow():
    return timezone.localdate() + timedelta(days=1)


@pytest.fixture
def draft_tour(dispatcher_client, tomorrow):
    # Osnutek z vozilom MB CD-456: nosilnost 1.200 kg in 4 paletna mesta
    return Tour.objects.create(
        dispatch_date=tomorrow,
        vehicle=Vehicle.objects.get(registration_number="MB CD-456"),
        driver=User.objects.get(email=DRIVER_MAJA_EMAIL),
        created_by=User.objects.get(email=DISPATCHER_EMAIL),
    )


@pytest.fixture
def big_truck(seeded):
    # Prosto vozilo, ki na noben datum še nima ture
    return Vehicle.objects.create(
        registration_number="MB XY-999", type=Vehicle.Type.TRUCK, max_load_kg=6000, pallet_spaces=16
    )


def add_order(tour, number, weight_kg, pallets):
    """Doda v turo novo naročilo z dano težo in paletami"""
    order = Order.objects.create(
        number=number,
        customer=Customer.objects.first(),
        received_date=tour.dispatch_date,
        dispatch_deadline=tour.dispatch_date,
        weight_kg=Decimal(weight_kg),
        pallets=Decimal(pallets),
    )
    add_stop(tour, order)


def get_tour(client, tour):
    return client.get(f"/api/tours/{tour.id}/").data


def test_load_equal_to_capacity_is_not_exceeded(dispatcher_client, draft_tour):
    add_order(draft_tour, "T-1", "700", "2.5")
    add_order(draft_tour, "T-2", "500", "1.5")
    data = get_tour(dispatcher_client, draft_tour)
    assert (data["total_weight_kg"], data["total_pallets"]) == (1200, 4)
    assert (data["weight_exceeded_by"], data["pallets_exceeded_by"]) == (0, 0)
    assert data["is_over_capacity"] is False


def test_too_many_pallets_shows_exceeded_amount(dispatcher_client, draft_tour):
    add_order(draft_tour, "T-1", "300", "5.5")
    data = get_tour(dispatcher_client, draft_tour)
    assert data["pallets_exceeded_by"] == Decimal("1.5")
    assert data["weight_exceeded_by"] == 0
    assert data["is_over_capacity"] is True


def test_too_much_weight_shows_exceeded_amount(dispatcher_client, draft_tour):
    add_order(draft_tour, "T-1", "1500", "2")
    data = get_tour(dispatcher_client, draft_tour)
    assert data["weight_exceeded_by"] == 300
    assert data["is_over_capacity"] is True


def test_tour_over_capacity_stays_draft(dispatcher_client, draft_tour):
    add_order(draft_tour, "T-1", "1500", "6")
    assert get_tour(dispatcher_client, draft_tour)["status"] == Tour.Status.DRAFT


def test_change_to_bigger_vehicle_fixes_capacity(dispatcher_client, draft_tour, big_truck):
    add_order(draft_tour, "T-1", "1500", "6")
    response = dispatcher_client.patch(f"/api/tours/{draft_tour.id}/", {"vehicle": big_truck.id})
    assert response.status_code == 200
    assert response.data["vehicle"]["registration_number"] == "MB XY-999"
    assert response.data["is_over_capacity"] is False


def test_cannot_change_to_vehicle_with_tour_on_same_date(dispatcher_client, draft_tour):
    busy = Vehicle.objects.get(registration_number="MB TR-789")
    response = dispatcher_client.patch(f"/api/tours/{draft_tour.id}/", {"vehicle": busy.id})
    assert response.status_code == 400
    assert "Vozilo ni aktivno ali ima na ta datum že turo" in response.data


def test_cannot_change_vehicle_of_confirmed_tour(dispatcher_client, big_truck, tomorrow):
    confirmed = Tour.objects.get(dispatch_date=tomorrow, status=Tour.Status.CONFIRMED)
    response = dispatcher_client.patch(f"/api/tours/{confirmed.id}/", {"vehicle": big_truck.id})
    assert response.status_code == 400
    assert "Vozilo je mogoče zamenjati samo v osnutku ture" in response.data


def test_driver_cannot_change_vehicle(driver_client, big_truck):
    tour = Tour.objects.filter(status=Tour.Status.DRAFT).first()
    response = driver_client.patch(f"/api/tours/{tour.id}/", {"vehicle": big_truck.id})
    assert response.status_code == 403
