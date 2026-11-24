import os
import pytest
import requests

BASE_URLS = {
    "user": os.getenv("USER_SERVICE_URL", "http" + "://" + "localhost:8001"),
    "product": os.getenv("PRODUCT_SERVICE_URL", "http" + "://" + "localhost:8002"),
    "order": os.getenv("ORDER_SERVICE_URL", "http" + "://" + "localhost:8003"),
    "payment": os.getenv("PAYMENT_SERVICE_URL", "http" + "://" + "localhost:8004"),
}


@pytest.mark.parametrize("service,base_url", BASE_URLS.items())
def test_health_check(service, base_url):
    response = requests.get(f"{base_url}/health", timeout=5)

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["database"] == "connected"


@pytest.mark.parametrize(
    "service,endpoint",
    [
        ("user", "/users"),
        ("product", "/products"),
        ("order", "/orders"),
        ("payment", "/payments"),
    ],
)
def test_empty_payload_rejected(service, endpoint):
    response = requests.post(
        f"{BASE_URLS[service]}{endpoint}",
        json={},
        timeout=5,
    )

    assert response.status_code == 422


import uuid


def test_complete_order_payment_flow():
    unique_id = uuid.uuid4().hex[:10]

    # 1. Create customer
    user_response = requests.post(
        f"{BASE_URLS['user']}/users",
        json={
            "name": f"Pytest Customer {unique_id}",
            "email": f"pytest_{unique_id}@example.com",
        },
        timeout=5,
    )
    assert user_response.status_code == 201
    user_id = user_response.json()["id"]

    # 2. Create product
    product_response = requests.post(
        f"{BASE_URLS['product']}/products",
        json={
            "name": f"Pytest Product {unique_id}",
            "price": "1500.00",
        },
        timeout=5,
    )
    assert product_response.status_code == 201
    product_id = product_response.json()["id"]

    # 3. Create order
    order_response = requests.post(
        f"{BASE_URLS['order']}/orders",
        json={
            "user_id": user_id,
            "product_id": product_id,
            "quantity": 2,
        },
        timeout=5,
    )
    assert order_response.status_code == 201
    order_id = order_response.json()["id"]

    # 4. Create simulated payment
    payment_response = requests.post(
        f"{BASE_URLS['payment']}/payments",
        json={
            "order_id": order_id,
            "amount": "3000.00",
            "method": "SIMULATED",
        },
        timeout=5,
    )
    assert payment_response.status_code == 201
    assert payment_response.json()["status"] == "SIMULATED_SUCCESS"

    # 5. Prevent duplicate payment
    duplicate_response = requests.post(
        f"{BASE_URLS['payment']}/payments",
        json={
            "order_id": order_id,
            "amount": "3000.00",
            "method": "SIMULATED",
        },
        timeout=5,
    )
    assert duplicate_response.status_code == 409

@pytest.mark.parametrize("service,base_url", BASE_URLS.items())
def test_metrics_endpoint(service, base_url):
    response = requests.get(f"{base_url}/metrics", timeout=5)

    assert response.status_code == 200
    assert "http_requests_total" in response.text
    assert "http_request_duration_seconds" in response.text
