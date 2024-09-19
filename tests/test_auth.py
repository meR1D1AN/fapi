import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# Тест для регистрации пользователя
def test_register_user():
    response = client.post(
        "/auth/register",
        json={
            "full_name": "Test User",
            "email": "test@example.com",
            "phone": "+79999999999",
            "password": "Password123!",
            "password_confirm": "Password123!"
        }
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Пользователь успешно зарегистрирован"}


# Тест для авторизации пользователя
def test_login():
    response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "Password123!"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
