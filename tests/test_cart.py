import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# Тест добавления товара в корзину
def test_add_to_cart():
    # Авторизация пользователя для работы с корзиной
    login_response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "Password123!"}
    )
    token = login_response.json()["access_token"]

    response = client.post(
        "/cart/",
        headers={"Authorization": f"Bearer {token}"},
        json={"product_id": 1, "quantity": 2}
    )
    assert response.status_code == 200


# Тест получения корзины
def test_get_cart():
    login_response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "Password123!"}
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/cart/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
