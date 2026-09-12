"""Tests for auth endpoints."""


def test_register(client):
    resp = client.post(
        "/api/auth/register",
        json={
            "email": "baru@catatuang.id",
            "full_name": "User Baru",
            "password": "rahasia123",
            "mode": "umkm",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "baru@catatuang.id"
    assert data["mode"] == "umkm"


def test_register_duplicate_email(client):
    payload = {
        "email": "duplikat@catatuang.id",
        "full_name": "User",
        "password": "pass",
        "mode": "personal",
    }
    client.post("/api/auth/register", json=payload)
    resp = client.post("/api/auth/register", json=payload)
    assert resp.status_code == 400


def test_login_success(client):
    client.post(
        "/api/auth/register",
        json={"email": "login@catatuang.id", "full_name": "Login User", "password": "secret"},
    )
    resp = client.post(
        "/api/auth/login",
        data={"username": "login@catatuang.id", "password": "secret"},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client):
    client.post(
        "/api/auth/register",
        json={"email": "wrongpass@catatuang.id", "full_name": "X", "password": "correct"},
    )
    resp = client.post(
        "/api/auth/login",
        data={"username": "wrongpass@catatuang.id", "password": "salah"},
    )
    assert resp.status_code == 401


def test_me_endpoint(client, auth_headers):
    resp = client.get("/api/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert "email" in resp.json()
