import pytest
from rest_framework.test import APIClient

from users.models import User

PASSWORD = "Geslo-12345"


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def dispatcher(db):
    return User.objects.create_user(
        "disponent@turaplan.si", PASSWORD, first_name="Ana", role=User.Role.DISPATCHER
    )


def login(client, email, password):
    return client.post("/api/auth/login/", {"email": email, "password": password})


def test_login_returns_tokens(client, dispatcher):
    response = login(client, dispatcher.email, PASSWORD)
    assert response.status_code == 200
    assert "access" in response.data and "refresh" in response.data


@pytest.mark.parametrize("email, password", [
    ("disponent@turaplan.si", "napacno-geslo"),
    ("neobstaja@turaplan.si", PASSWORD),
])
def test_wrong_credentials_give_same_message(client, dispatcher, email, password):
    response = login(client, email, password)
    assert response.status_code == 401
    assert response.data["detail"] == "Napačna e-pošta ali geslo"


def test_inactive_user_cannot_login(client, dispatcher):
    dispatcher.is_active = False
    dispatcher.save()
    response = login(client, dispatcher.email, PASSWORD)
    assert response.status_code == 401


def test_me_requires_login(client, db):
    assert client.get("/api/auth/me/").status_code == 401


def test_me_returns_user_with_role(client, dispatcher):
    token = login(client, dispatcher.email, PASSWORD).data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    response = client.get("/api/auth/me/")
    assert response.status_code == 200
    assert response.data["role"] == "DISPATCHER"


def test_token_stops_working_after_deactivation(client, dispatcher):
    token = login(client, dispatcher.email, PASSWORD).data["access"]
    dispatcher.is_active = False
    dispatcher.save()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    assert client.get("/api/auth/me/").status_code == 401


def test_only_admin_role_can_use_django_admin(db):
    admin = User.objects.create_superuser("admin@turaplan.si", PASSWORD)
    driver = User.objects.create_user("voznik@turaplan.si", PASSWORD, role=User.Role.DRIVER)
    assert admin.role == User.Role.ADMIN and admin.is_staff
    assert not driver.is_staff
