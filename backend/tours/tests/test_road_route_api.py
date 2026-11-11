import pytest

from tours.tests.test_suggested_order_api import accept, line_tour, numbers, suggestion  # noqa: F401


@pytest.fixture
def fake_osrm(monkeypatch):
    """Lažni OSRM: pot dolga 12,34 km in 20 minut, po cesti je najbližja stranka N-016"""
    calls = []

    def osrm(service, points, params):
        calls.append((service, points))
        if service == "route":
            return {
                "code": "Ok",
                "routes": [{
                    "distance": 12340,
                    "duration": 1200,
                    "geometry": {"coordinates": [[15.0, 46.0], [15.1, 46.2]]},
                }],
            }
        # Točke tabele: 0 skladišče, 1 N-016, 2 N-014 in N-024, 3 N-015
        return {"code": "Ok", "distances": [[0, 1, 9, 5], [1, 0, 2, 9], [9, 2, 0, 3], [5, 9, 3, 0]]}

    monkeypatch.setattr("tours.services.osrm", osrm)
    return calls


def route(client, tour):
    return client.get(f"/api/tours/{tour.id}/route/")


def test_route_returns_road_distance_duration_and_line(dispatcher_client, line_tour, fake_osrm):
    response = route(dispatcher_client, line_tour)
    assert response.status_code == 200
    # Točke črte so obrnjene iz lng,lat v lat,lng
    assert response.data["road"] == {
        "distance_km": 12.3, "duration_min": 20, "geometry": [[46.0, 15.0], [46.2, 15.1]],
    }


def test_route_goes_from_warehouse_through_stops_in_order(dispatcher_client, line_tour, fake_osrm):
    route(dispatcher_client, line_tour)
    service, points = fake_osrm[0]
    assert service == "route"
    # Skladišče, N-016, N-014 in N-024 iste stranke, N-015
    assert [float(lat) for lat, lng in points] == [46.0, 46.3, 46.1, 46.1, 46.2]


def test_route_is_empty_when_osrm_is_unavailable(dispatcher_client, line_tour):
    response = route(dispatcher_client, line_tour)
    assert response.status_code == 200
    assert response.data == {"road": None}


def test_route_is_empty_for_tour_without_stops(dispatcher_client, draft_tour, fake_osrm):
    assert route(dispatcher_client, draft_tour).data == {"road": None}
    assert fake_osrm == []


def test_driver_cannot_request_route(driver_client, line_tour):
    assert route(driver_client, line_tour).status_code == 403


def test_suggestion_uses_road_distances_when_available(dispatcher_client, line_tour, fake_osrm):
    data = suggestion(dispatcher_client, line_tour).data
    # Po zraku bi bil prvi N-014, po cestni tabeli pa je skladišču najbližji N-016
    assert numbers(data["stops"]) == ["N-016", "N-014", "N-024", "N-015"]
    assert data["road"]["distance_km"] == 12.3


def test_suggestion_falls_back_to_air_distance_without_osrm(dispatcher_client, line_tour):
    data = suggestion(dispatcher_client, line_tour).data
    assert numbers(data["stops"]) == ["N-014", "N-024", "N-015", "N-016"]
    assert data["road"] is None


def test_suggestion_ignores_road_table_with_missing_connection(dispatcher_client, line_tour, monkeypatch):
    table = {"code": "Ok", "distances": [[0, None, 9, 5], [1, 0, 2, 9], [9, 2, 0, 3], [5, 9, 3, 0]]}
    monkeypatch.setattr(
        "tours.services.osrm", lambda service, points, params: table if service == "table" else None,
    )
    assert numbers(suggestion(dispatcher_client, line_tour).data["stops"]) == ["N-014", "N-024", "N-015", "N-016"]


def test_accepted_suggestion_saves_exactly_the_shown_order(dispatcher_client, line_tour, fake_osrm):
    stop_ids = [stop["id"] for stop in suggestion(dispatcher_client, line_tour).data["stops"]]
    response = accept(dispatcher_client, line_tour, stop_ids)
    assert numbers(response.data["stops"]) == ["N-016", "N-014", "N-024", "N-015"]


def test_suggestion_that_no_longer_matches_tour_is_rejected(dispatcher_client, line_tour):
    stop_ids = [stop["id"] for stop in suggestion(dispatcher_client, line_tour).data["stops"]]
    response = accept(dispatcher_client, line_tour, stop_ids[:-1])
    assert response.status_code == 400
    assert response.data == ["Predlog ne ustreza več postankom ture, zahtevaj nov predlog"]
