import pytest

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret-key"

    with app.test_client() as client:
        yield client


def test_login_page(client):
    response = client.get("/login")

    assert response.status_code == 200
    assert b"Sign in" in response.data
    assert b"Username" in response.data
    assert b"Password" in response.data


def test_login_success(client):
    response = client.post(
        "/login",
        data={
            "username": "admin",
            "password": "Admin@123"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Xin ch" in response.data

    with client.session_transaction() as session:
        assert session["user_id"] == 1
        assert session["username"] == "admin"


def test_login_wrong_password(client):
    response = client.post(
        "/login",
        data={
            "username": "admin",
            "password": "WrongPassword"
        }
    )

    assert response.status_code == 200
    assert b"kh" in response.data

    with client.session_transaction() as session:
        assert "user_id" not in session


def test_login_wrong_username(client):
    response = client.post(
        "/login",
        data={
            "username": "unknown",
            "password": "Admin@123"
        }
    )

    assert response.status_code == 200

    with client.session_transaction() as session:
        assert "user_id" not in session


def test_logout(client):
    # Login trước
    client.post(
        "/login",
        data={
            "username": "admin",
            "password": "Admin@123"
        }
    )

    # Logout
    response = client.get(
        "/logout",
        follow_redirects=True
    )

    assert response.status_code == 200

    with client.session_transaction() as session:
        assert "user_id" not in session