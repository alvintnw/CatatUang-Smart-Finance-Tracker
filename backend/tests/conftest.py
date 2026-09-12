"""
Shared pytest fixtures — SQLite database so tests require no PostgreSQL.

IMPORTANT: The DATABASE_URL env var must be set before app.config is imported
because pydantic-settings reads env vars at Settings() instantiation time.
We set it here before any app import.
"""
import os

# Must be set before ANY app.* import — pydantic-settings reads this at class
# instantiation time inside app/config.py
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

TEST_DB_URL = "sqlite:///./test.db"
# Use StaticPool so all connections share the same in-memory-like SQLite DB
from sqlalchemy.pool import StaticPool  # noqa: E402
engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Patch app.database module BEFORE importing app.main (which triggers SQLAlchemy
# model registration, but the engine itself is used at request time via get_db)
import app.database as _app_db  # noqa: E402
_app_db.engine = engine
_app_db.SessionLocal = TestingSessionLocal

from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    # Seed categories
    db = TestingSessionLocal()
    from app.models import Category

    seeds = [
        Category(id=1,  name="Makanan & Minuman", slug="makanan"),
        Category(id=2,  name="Transportasi",      slug="transportasi"),
        Category(id=3,  name="Tagihan & Utilitas", slug="tagihan"),
        Category(id=4,  name="Belanja",            slug="belanja"),
        Category(id=5,  name="Hiburan",            slug="hiburan"),
        Category(id=6,  name="Pendidikan",         slug="pendidikan"),
        Category(id=7,  name="Kesehatan",          slug="kesehatan"),
        Category(id=8,  name="Gaji & Pendapatan",  slug="gaji"),
        Category(id=9,  name="Lain-lain",          slug="lain-lain"),
    ]
    db.add_all(seeds)
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    """
    Test client that overrides get_db to use a fresh SQLite session per request.
    Using a fresh session each time ensures committed data is visible across requests.
    """
    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers(client):
    """Register + login, return Authorization header dict."""
    client.post(
        "/api/auth/register",
        json={
            "email": "test@catatuang.id",
            "full_name": "Test User",
            "password": "password123",
            "mode": "personal",
        },
    )
    resp = client.post(
        "/api/auth/login",
        data={"username": "test@catatuang.id", "password": "password123"},
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
