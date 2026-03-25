import os
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models import Base
from app.storage import get_db

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(setup_db):
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    client.post("/auth/register", json={"username": "testuser", "password": "testpass"})
    response = client.post("/auth/login", data={"username": "testuser", "password": "testpass"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# --- Auth tests ---

def test_register(client):
    response = client.post("/auth/register", json={"username": "alice", "password": "secret"})
    assert response.status_code == 201


def test_register_duplicate(client):
    client.post("/auth/register", json={"username": "alice", "password": "secret"})
    response = client.post("/auth/register", json={"username": "alice", "password": "secret"})
    assert response.status_code == 400


def test_login(client):
    client.post("/auth/register", json={"username": "alice", "password": "secret"})
    response = client.post("/auth/login", data={"username": "alice", "password": "secret"})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(client):
    client.post("/auth/register", json={"username": "alice", "password": "secret"})
    response = client.post("/auth/login", data={"username": "alice", "password": "wrong"})
    assert response.status_code == 401


# --- Index ---

def test_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello world"}


# --- Todo tests (require auth) ---

def test_get_todos_unauthenticated(client):
    response = client.get("/todos")
    assert response.status_code == 401


def test_get_todos_empty(client, auth_headers):
    response = client.get("/todos", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_create_todo(client, auth_headers):
    response = client.post("/todos", json={"name": "Sport", "description": "Go to gym"}, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Sport"
    assert data["description"] == "Go to gym"
    assert "id" in data


def test_get_todos(client, auth_headers):
    client.post("/todos", json={"name": "Sport", "description": "Go to gym"}, headers=auth_headers)
    client.post("/todos", json={"name": "Study", "description": "Read a book"}, headers=auth_headers)
    response = client.get("/todos", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_todo_existing(client, auth_headers):
    created = client.post("/todos", json={"name": "Sport", "description": "Go to gym"}, headers=auth_headers).json()
    response = client.get(f"/todos/{created['id']}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Sport"


def test_get_todo_not_found(client, auth_headers):
    response = client.get("/todos/999", headers=auth_headers)
    assert response.status_code == 404


def test_get_todo_invalid_id(client, auth_headers):
    response = client.get("/todos/abc", headers=auth_headers)
    assert response.status_code == 422


def test_update_todo_existing(client, auth_headers):
    created = client.post("/todos", json={"name": "Sport", "description": "Go to gym"}, headers=auth_headers).json()
    response = client.put(f"/todos/{created['id']}", json={"name": "Exercise"}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Exercise"
    assert response.json()["description"] == "Go to gym"


def test_update_todo_not_found(client, auth_headers):
    response = client.put("/todos/999", json={"name": "Test"}, headers=auth_headers)
    assert response.status_code == 404


def test_update_todo_invalid_id(client, auth_headers):
    response = client.put("/todos/abc", json={"name": "Test"}, headers=auth_headers)
    assert response.status_code == 422


def test_delete_todo_existing(client, auth_headers):
    created = client.post("/todos", json={"name": "Sport", "description": "Go to gym"}, headers=auth_headers).json()
    response = client.delete(f"/todos/{created['id']}", headers=auth_headers)
    assert response.status_code == 204
    assert client.get(f"/todos/{created['id']}", headers=auth_headers).status_code == 404


def test_delete_todo_not_found(client, auth_headers):
    response = client.delete("/todos/999", headers=auth_headers)
    assert response.status_code == 404
