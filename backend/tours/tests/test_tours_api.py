from datetime import timedelta

import pytest
from django.core.management import call_command
from django.utils import timezone
from rest_framework.test import APIClient

from tours.models import Tour
from users.models import User


@pytest.fixture
def seeded(db):
    # Testni podatki: včeraj zaključena, danes v dostavi, jutri potrjena in osnutek
    call_command("seed_data", stdout=None)


def client_for(email):
    client = APIClient()
    client.force_authenticate(User.objects.get(email=email))
    return client


@pytest.fixture
def dispatcher_client(seeded):
    return client_for("disponent@turaplan.si")


def today_tour():
    return Tour.objects.get(dispatch_date=timezone.localdate())


def test_tour_list_without_filters_shows_all_tours_by_date(dispatcher_client):
    response = dispatcher_client.get("/api/tours/")
    assert response.status_code == 200
    dates = [tour["dispatch_date"] for tour in response.data]
    assert len(dates) == 4
    assert dates == sorted(dates)


def test_tour_list_from_today_hides_past_tours(dispatcher_client):
    today = timezone.localdate()
    response = dispatcher_client.get(f"/api/tours/?date_from={today}")
    assert len(response.data) == 3
    assert min(tour["dispatch_date"] for tour in response.data) == str(today)


def test_tour_list_can_be_filtered_by_date_range(dispatcher_client):
    yesterday = timezone.localdate() - timedelta(days=1)
    today = timezone.localdate()
    response = dispatcher_client.get(f"/api/tours/?date_from={yesterday}&date_to={today}")
    assert [tour["status"] for tour in response.data] == ["COMPLETED", "IN_DELIVERY"]


def test_tour_list_can_be_filtered_by_status(dispatcher_client):
    response = dispatcher_client.get("/api/tours/?status=DRAFT")
    assert [tour["status"] for tour in response.data] == ["DRAFT"]


def test_invalid_date_filter_returns_400(dispatcher_client):
    assert dispatcher_client.get("/api/tours/?date_from=abc").status_code == 400


def test_tour_list_contains_load_and_delivery_progress(dispatcher_client):
    tour = next(t for t in dispatcher_client.get("/api/tours/").data if t["status"] == "IN_DELIVERY")
    assert tour["vehicle"]["max_load_kg"] == 1200
    assert tour["total_weight_kg"] == 1100
    assert tour["total_pallets"] == 3.75
    assert (tour["stop_count"], tour["delivered_count"], tour["not_delivered_count"]) == (4, 2, 1)


def test_tour_detail_contains_stops_with_result_and_reason(dispatcher_client):
    response = dispatcher_client.get(f"/api/tours/{today_tour().id}/")
    stops = response.data["stops"]
    assert [stop["sequence"] for stop in stops] == [1, 2, 3, 4]
    assert stops[2]["result"] == "NOT_DELIVERED"
    assert stops[2]["reason"] == "Ni bilo nikogar"
    assert stops[2]["marked_at"] is not None
    assert stops[3]["marked_at"] is None


def test_driver_cannot_see_dispatcher_tour_list(seeded):
    response = client_for("voznik@turaplan.si").get("/api/tours/")
    assert response.status_code == 403


def test_anonymous_user_cannot_see_tour_detail(seeded):
    assert APIClient().get(f"/api/tours/{today_tour().id}/").status_code == 401
