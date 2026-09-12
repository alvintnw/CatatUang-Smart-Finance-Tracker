"""Tests for transaction CRUD endpoints."""
import pytest


def test_create_transaction_income(client, auth_headers):
    resp = client.post(
        "/api/transactions",
        json={
            "amount": 5000000,
            "type": "income",
            "description": "gaji bulan ini dari kantor",
            "date": "2024-06-01",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["type"] == "income"
    assert data["category"]["slug"] == "gaji"
    assert data["corrected_by_user"] is False


def test_create_transaction_expense_auto_categorise(client, auth_headers):
    resp = client.post(
        "/api/transactions",
        json={
            "amount": 45000,
            "type": "expense",
            "description": "beli kopi starbucks",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["category"]["slug"] == "makanan"


def test_create_transaction_lain_lain(client, auth_headers):
    resp = client.post(
        "/api/transactions",
        json={
            "amount": 10000,
            "type": "expense",
            "description": "pembayaran entah apa",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["category"]["slug"] == "lain-lain"


def test_list_transactions(client, auth_headers):
    resp = client.get("/api/transactions", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_update_transaction(client, auth_headers):
    # Create first
    create_resp = client.post(
        "/api/transactions",
        json={"amount": 20000, "type": "expense", "description": "makan siang"},
        headers=auth_headers,
    )
    tx_id = create_resp.json()["id"]

    # Update amount
    update_resp = client.put(
        f"/api/transactions/{tx_id}",
        json={"amount": 25000},
        headers=auth_headers,
    )
    assert update_resp.status_code == 200
    assert float(update_resp.json()["amount"]) == 25000.0


def test_correct_category(client, auth_headers):
    # Create transaction (auto-categorised as makanan)
    create_resp = client.post(
        "/api/transactions",
        json={"amount": 50000, "type": "expense", "description": "beli buku starbucks"},
        headers=auth_headers,
    )
    tx_id = create_resp.json()["id"]

    # Correct to pendidikan (id=6)
    corr_resp = client.post(
        f"/api/transactions/{tx_id}/correct-category",
        json={"transaction_id": tx_id, "corrected_category_id": 6},
        headers=auth_headers,
    )
    assert corr_resp.status_code == 200
    data = corr_resp.json()
    assert data["category"]["slug"] == "pendidikan"
    assert data["corrected_by_user"] is True


def test_delete_transaction(client, auth_headers):
    create_resp = client.post(
        "/api/transactions",
        json={"amount": 5000, "type": "expense", "description": "parkir motor"},
        headers=auth_headers,
    )
    tx_id = create_resp.json()["id"]

    del_resp = client.delete(f"/api/transactions/{tx_id}", headers=auth_headers)
    assert del_resp.status_code == 204

    get_resp = client.get(f"/api/transactions/{tx_id}", headers=auth_headers)
    assert get_resp.status_code == 404


def test_create_transaction_requires_auth(client):
    resp = client.post(
        "/api/transactions",
        json={"amount": 10000, "type": "expense", "description": "test"},
    )
    assert resp.status_code == 401


def test_create_transaction_invalid_amount(client, auth_headers):
    resp = client.post(
        "/api/transactions",
        json={"amount": -1000, "type": "expense", "description": "invalid"},
        headers=auth_headers,
    )
    assert resp.status_code == 422


def test_umkm_transaction(client, auth_headers):
    resp = client.post(
        "/api/transactions",
        json={
            "amount": 150000,
            "type": "income",
            "description": "penjualan ke bu siti",
            "customer_name": "Bu Siti",
            "payment_method": "qris",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["customer_name"] == "Bu Siti"
    assert data["payment_method"] == "qris"
