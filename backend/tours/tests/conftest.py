import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

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
