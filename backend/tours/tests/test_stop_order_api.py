from tours.models import Order, Stop


def add(client, tour, number):
    """Doda naročilo v turo in vrne odgovor API"""
    return client.post(f"/api/tours/{tour.id}/stops/", {"order": Order.objects.get(number=number).id})


def stop_id(tour, number):
    return Stop.objects.get(tour=tour, order__number=number).id


def numbers(data):
    return [stop["order_number"] for stop in data["stops"]]


def test_move_stop_down_and_up(dispatcher_client, draft_tour):
    for number in ["N-014", "N-015", "N-016"]:
        add(dispatcher_client, draft_tour, number)
    response = dispatcher_client.post(f"/api/stops/{stop_id(draft_tour, 'N-014')}/move/", {"direction": "down"})
    assert response.status_code == 200
    assert numbers(response.data) == ["N-015", "N-014", "N-016"]
    assert [stop["sequence"] for stop in response.data["stops"]] == [1, 2, 3]

    response = dispatcher_client.post(f"/api/stops/{stop_id(draft_tour, 'N-016')}/move/", {"direction": "up"})
    assert numbers(response.data) == ["N-015", "N-016", "N-014"]


def test_first_stop_cannot_move_up(dispatcher_client, draft_tour):
    add(dispatcher_client, draft_tour, "N-014")
    response = dispatcher_client.post(f"/api/stops/{stop_id(draft_tour, 'N-014')}/move/", {"direction": "up"})
    assert response.status_code == 400
    assert "Postanek je že na prvem mestu" in response.data


def test_order_of_same_customer_goes_after_its_last_stop(dispatcher_client, draft_tour):
    # N-014 in N-024 sta naročili Pekarne Klas, N-015 je Gostilna Lipa
    add(dispatcher_client, draft_tour, "N-014")
    add(dispatcher_client, draft_tour, "N-015")
    response = add(dispatcher_client, draft_tour, "N-024")
    assert numbers(response.data) == ["N-014", "N-024", "N-015"]
    assert [stop["sequence"] for stop in response.data["stops"]] == [1, 2, 3]
    assert response.data["split_customers"] == []


def test_split_customer_stops_are_reported(dispatcher_client, draft_tour):
    for number in ["N-014", "N-015", "N-024"]:
        add(dispatcher_client, draft_tour, number)
    response = dispatcher_client.post(f"/api/stops/{stop_id(draft_tour, 'N-024')}/move/", {"direction": "down"})
    assert numbers(response.data) == ["N-014", "N-015", "N-024"]
    assert response.data["split_customers"] == ["Pekarna Klas"]


def test_driver_note_is_saved(dispatcher_client, draft_tour):
    add(dispatcher_client, draft_tour, "N-014")
    response = dispatcher_client.patch(
        f"/api/stops/{stop_id(draft_tour, 'N-014')}/", {"driver_note": "Pokliči 10 minut prej"}
    )
    assert response.status_code == 200
    assert response.data["stops"][0]["driver_note"] == "Pokliči 10 minut prej"


def test_too_long_driver_note_is_not_saved(dispatcher_client, draft_tour):
    add(dispatcher_client, draft_tour, "N-014")
    stop = stop_id(draft_tour, "N-014")
    response = dispatcher_client.patch(f"/api/stops/{stop}/", {"driver_note": "a" * 302})
    assert response.status_code == 400
    assert "Opomba je predolga za 2 znaka" in response.data
    assert Stop.objects.get(pk=stop).driver_note == ""


def test_stop_shows_customer_delivery_note(dispatcher_client, draft_tour):
    # Pekarna Zrno ima stalno opombo za dostavo
    response = add(dispatcher_client, draft_tour, "N-023")
    assert response.data["stops"][0]["delivery_note"] == "Zadnji vhod, zvoniti 2x"


def test_driver_cannot_move_stop(driver_client):
    stop = Stop.objects.first()
    response = driver_client.post(f"/api/stops/{stop.id}/move/", {"direction": "down"})
    assert response.status_code == 403


def test_stop_can_be_dragged_to_any_position(dispatcher_client, draft_tour):
    for number in ["N-014", "N-015", "N-016", "N-019"]:
        add(dispatcher_client, draft_tour, number)
    url = f"/api/stops/{stop_id(draft_tour, 'N-019')}/move/"
    response = dispatcher_client.post(url, {"position": 1})
    assert response.status_code == 200
    assert numbers(response.data) == ["N-019", "N-014", "N-015", "N-016"]
    assert [stop["sequence"] for stop in response.data["stops"]] == [1, 2, 3, 4]

    response = dispatcher_client.post(f"/api/stops/{stop_id(draft_tour, 'N-014')}/move/", {"position": 4})
    assert numbers(response.data) == ["N-019", "N-015", "N-016", "N-014"]


def test_stop_cannot_be_moved_outside_tour(dispatcher_client, draft_tour):
    add(dispatcher_client, draft_tour, "N-014")
    response = dispatcher_client.post(f"/api/stops/{stop_id(draft_tour, 'N-014')}/move/", {"position": 2})
    assert response.status_code == 400
    assert "Mesto mora biti med 1 in 1" in response.data


def test_driver_note_can_be_saved_as_customer_delivery_note(dispatcher_client, draft_tour):
    add(dispatcher_client, draft_tour, "N-014")
    stop = stop_id(draft_tour, "N-014")
    dispatcher_client.patch(f"/api/stops/{stop}/", {"driver_note": "Rampa za trgovino"})
    url = f"/api/stops/{stop}/delivery-note/"
    response = dispatcher_client.post(url, {"delivery_note": "Rampa za trgovino"})
    assert response.status_code == 200
    assert response.data["stops"][0]["delivery_note"] == "Rampa za trgovino"
    # Opomba je zdaj pri stranki, zato je pri postanku ne podvajamo
    assert response.data["stops"][0]["driver_note"] == ""
    assert Order.objects.get(number="N-014").customer.delivery_note == "Rampa za trgovino"


def test_customer_delivery_note_can_be_removed(dispatcher_client, draft_tour):
    add(dispatcher_client, draft_tour, "N-023")
    url = f"/api/stops/{stop_id(draft_tour, 'N-023')}/delivery-note/"
    response = dispatcher_client.post(url, {"delivery_note": ""})
    assert response.data["stops"][0]["delivery_note"] == ""
