from datetime import timedelta

import pytest
from django.core.management import call_command
from django.utils import timezone
from rest_framework.test import APIClient

from tours.models import Tour, Vehicle
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


@pytest.fixture
def driver_client(seeded):
    return client_for("voznik@turaplan.si")


@pytest.fixture
def tomorrow():
    return timezone.localdate() + timedelta(days=1)


@pytest.fixture
def draft_tour(dispatcher_client, tomorrow):
    # Nova tura z vozilom in voznikom, ki jutri še nimata ture
    response = dispatcher_client.post("/api/tours/", {
        "dispatch_date": tomorrow,
        "vehicle": Vehicle.objects.get(registration_number="MB CD-456").id,
        "driver": User.objects.get(email="voznik2@turaplan.si").id,
    })
    assert response.status_code == 201
    return Tour.objects.get(pk=response.data["id"])
