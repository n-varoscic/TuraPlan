from django.utils import timezone

from tours.models import Order, Stop, Tour
from tours.services import format_pallets


def add(client, tour, number):
    return client.post(f"/api/tours/{tour.id}/stops/", {"order": Order.objects.get(number=number).id})


def confirm(client, tour):
    return client.post(f"/api/tours/{tour.id}/confirm/")


def test_tour_is_confirmed_and_confirmation_time_saved(dispatcher_client, draft_tour):
    add(dispatcher_client, draft_tour, "N-014")
    response = confirm(dispatcher_client, draft_tour)
    assert response.status_code == 200
    assert response.data["status"] == Tour.Status.CONFIRMED
    draft_tour.refresh_from_db()
    assert draft_tour.confirmed_at is not None


def test_tour_without_stops_cannot_be_confirmed(dispatcher_client, draft_tour):
    response = confirm(dispatcher_client, draft_tour)
    assert response.status_code == 400
    assert response.data == ["Tura nima nobenega postanka"]


def test_tour_over_capacity_shows_all_unmet_conditions(dispatcher_client, draft_tour):
    # N-021 ima 1.800 kg in 5,5 palete, vozilo pa 1.200 kg in 4 paletna mesta
    add(dispatcher_client, draft_tour, "N-021")
    response = confirm(dispatcher_client, draft_tour)
    assert response.status_code == 400
    assert response.data == [
        "Kapaciteta je presežena za 600 kg",
        "Kapaciteta je presežena za 1,5 palete",
    ]
    assert dispatcher_client.get(f"/api/tours/{draft_tour.id}/").data["confirmation_errors"] == response.data
    draft_tour.refresh_from_db()
    assert draft_tour.status == Tour.Status.DRAFT


def test_pallets_are_written_in_correct_form():
    assert [format_pallets(n) for n in [1, 2, 3, 5, "1.5", "0.25"]] == [
        "1 paleto", "2 paleti", "3 palete", "5 palet", "1,5 palete", "0,25 palete",
    ]


def test_confirmed_tour_cannot_be_changed(dispatcher_client, draft_tour):
    add(dispatcher_client, draft_tour, "N-014")
    add(dispatcher_client, draft_tour, "N-015")
    confirm(dispatcher_client, draft_tour)
    stop = Stop.objects.filter(tour=draft_tour).first()
    responses = [
        add(dispatcher_client, draft_tour, "N-016"),
        dispatcher_client.delete(f"/api/stops/{stop.id}/"),
        dispatcher_client.post(f"/api/stops/{stop.id}/move/", {"position": 2}),
        dispatcher_client.patch(f"/api/stops/{stop.id}/", {"driver_note": "Nova opomba"}),
        dispatcher_client.post(f"/api/stops/{stop.id}/delivery-note/", {"delivery_note": "Nova opomba"}),
    ]
    for response in responses:
        assert response.status_code == 400
        assert response.data == ["Turo je mogoče spreminjati samo v osnutku"]
    assert Stop.objects.filter(tour=draft_tour).count() == 2


def test_confirmed_tour_can_be_returned_to_draft(dispatcher_client, draft_tour):
    add(dispatcher_client, draft_tour, "N-014")
    confirm(dispatcher_client, draft_tour)
    response = dispatcher_client.post(f"/api/tours/{draft_tour.id}/unconfirm/")
    assert response.status_code == 200
    assert response.data["status"] == Tour.Status.DRAFT
    assert response.data["confirmed_at"] is None


def test_started_tour_cannot_be_returned_to_draft(dispatcher_client):
    started = Tour.objects.get(dispatch_date=timezone.localdate(), status=Tour.Status.IN_DELIVERY)
    response = dispatcher_client.post(f"/api/tours/{started.id}/unconfirm/")
    assert response.status_code == 400
    assert response.data == ["Voznik je turo že začel, zato je ni mogoče vrniti v osnutek"]


def test_driver_cannot_confirm_tour(driver_client):
    tour = Tour.objects.filter(status=Tour.Status.DRAFT).first()
    assert driver_client.post(f"/api/tours/{tour.id}/confirm/").status_code == 403
