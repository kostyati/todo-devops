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


def test_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello world"}


def test_get_todos_empty(client):
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == []


def test_create_todo(client):
    response = client.post("/todos", json={"name": "Sport", "description": "Go to gym"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Sport"
    assert data["description"] == "Go to gym"
    assert "id" in data


def test_get_todos(client):
    client.post("/todos", json={"name": "Sport", "description": "Go to gym"})
    client.post("/todos", json={"name": "Study", "description": "Read a book"})
    response = client.get("/todos")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_todo_existing(client):
    created = client.post("/todos", json={"name": "Sport", "description": "Go to gym"}).json()
    response = client.get(f"/todos/{created['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "Sport"


def test_get_todo_not_found(client):
    response = client.get("/todos/999")
    assert response.status_code == 404


def test_get_todo_invalid_id(client):
    response = client.get("/todos/abc")
    assert response.status_code == 422


def test_update_todo_existing(client):
    created = client.post("/todos", json={"name": "Sport", "description": "Go to gym"}).json()
    response = client.put(f"/todos/{created['id']}", json={"name": "Exercise"})
    assert response.status_code == 200
    assert response.json()["name"] == "Exercise"
    assert response.json()["description"] == "Go to gym"


def test_update_todo_not_found(client):
    response = client.put("/todos/999", json={"name": "Test"})
    assert response.status_code == 404


def test_update_todo_invalid_id(client):
    response = client.put("/todos/abc", json={"name": "Test"})
    assert response.status_code == 422
