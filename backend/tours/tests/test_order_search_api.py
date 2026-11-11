from tours.management.commands.seed_data import DRIVER_VID_EMAIL
from tours.models import Order, Tour
from users.models import User


def search(client, query):
    return client.get("/api/orders/search/", {"q": query})


def numbers(response):
    return [order["number"] for order in response.data]


def test_search_by_order_number_returns_exact_match(dispatcher_client):
    response = search(dispatcher_client, "N-013")
    assert response.status_code == 200
    assert numbers(response) == ["N-013"]


def test_search_by_order_number_ignores_case_and_spaces(dispatcher_client):
    assert numbers(search(dispatcher_client, " n-013 ")) == ["N-013"]


def test_part_of_order_number_is_not_a_match(dispatcher_client):
    assert numbers(search(dispatcher_client, "N-01")) == []


def test_search_by_customer_name_returns_partial_matches_ignoring_case(dispatcher_client):
    results = search(dispatcher_client, "gorjan").data
    # Pekarna Gorjanci ima naročili N-011 in N-012; zadetki so lahko tudi druge stranke z »gorjan« v nazivu
    assert {"N-011", "N-012"} <= {order["number"] for order in results}
    assert all("gorjan" in order["customer"].lower() for order in results)


def test_customer_search_needs_at_least_three_characters(dispatcher_client):
    assert numbers(search(dispatcher_client, "pe")) == []
    assert len(numbers(search(dispatcher_client, "pek"))) > 0


def test_empty_search_returns_nothing(dispatcher_client):
    assert numbers(search(dispatcher_client, "")) == []
    assert numbers(search(dispatcher_client, "ni take stranke")) == []


def test_result_shows_customer_deadline_and_status(dispatcher_client):
    order = Order.objects.get(number="N-013")
    result = search(dispatcher_client, "N-013").data[0]
    assert result["customer"] == order.customer.name
    assert result["dispatch_deadline"] == str(order.dispatch_deadline)
    assert result["status"] == "NEW"


def test_planned_order_shows_tour_date_and_driver(dispatcher_client, tomorrow):
    # N-011 je v jutrišnjem osnutku voznika Vida
    result = search(dispatcher_client, "N-011").data[0]
    tour = Tour.objects.get(dispatch_date=tomorrow, status=Tour.Status.DRAFT)
    driver = User.objects.get(email=DRIVER_VID_EMAIL)
    assert result["status"] == "PLANNED"
    assert result["tour"] == {
        "id": tour.id,
        "dispatch_date": tomorrow,
        "driver": f"{driver.first_name} {driver.last_name}",
    }


def test_unassigned_order_has_no_tour(dispatcher_client):
    result = search(dispatcher_client, "N-013").data[0]
    assert result["tour"] is None
    assert result["not_delivered_reason"] == ""


def test_not_delivered_order_shows_reason_of_last_attempt(dispatcher_client):
    result = search(dispatcher_client, "N-003").data[0]
    assert result["status"] == "NOT_DELIVERED"
    assert result["not_delivered_reason"] == "Stranka zaprta"
    # Naročilo čaka na ponovno planiranje, zato ni v nobeni turi
    assert result["tour"] is None


def test_replanned_order_shows_new_tour_without_old_reason(dispatcher_client, draft_tour):
    order = Order.objects.get(number="N-003")
    dispatcher_client.post(f"/api/tours/{draft_tour.id}/stops/", {"order": order.id})
    result = search(dispatcher_client, "N-003").data[0]
    assert result["status"] == "PLANNED"
    assert result["tour"]["id"] == draft_tour.id
    assert result["not_delivered_reason"] == ""


def test_driver_cannot_search_orders(driver_client):
    assert search(driver_client, "N-013").status_code == 403
