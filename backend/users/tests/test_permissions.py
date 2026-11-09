import pytest
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.views import APIView

from users.models import User
from users.permissions import IsDispatcher, IsDriver


# Preprosta pogleda samo za test pravic
class DispatcherOnlyView(APIView):
    permission_classes = [IsDispatcher]

    def get(self, request):
        return Response({"ok": True})


class DriverOnlyView(APIView):
    permission_classes = [IsDriver]

    def get(self, request):
        return Response({"ok": True})


def call(view, user=None):
    request = APIRequestFactory().get("/test/")
    if user:
        force_authenticate(request, user=user)
    return view.as_view()(request)


@pytest.fixture
def dispatcher(db):
    return User.objects.create_user("disponent@turaplan.si", "x", role=User.Role.DISPATCHER)


@pytest.fixture
def driver(db):
    return User.objects.create_user("voznik@turaplan.si", "x", role=User.Role.DRIVER)


def test_anonymous_user_gets_401(db):
    assert call(DispatcherOnlyView).status_code == 401


def test_dispatcher_has_access_to_dispatcher_view(dispatcher):
    assert call(DispatcherOnlyView, dispatcher).status_code == 200


def test_driver_gets_403_on_dispatcher_view(driver):
    response = call(DispatcherOnlyView, driver)
    assert response.status_code == 403
    assert response.data["detail"] == "Ni dostopa"


def test_dispatcher_gets_403_on_driver_view(dispatcher):
    assert call(DriverOnlyView, dispatcher).status_code == 403
