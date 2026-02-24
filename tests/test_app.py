import pytest
from fastapi.testclient import TestClient
from app.main import app, pseudo_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_db():
    # Reset pseudo_db to initial state before each test
    global pseudo_db
    pseudo_db = [
        {"id": 1, "name": "Sport", "description": "GO  to gym"},
        {"id": 2, "name": "Study", "description": "Read a book"},
        {"id": 3, "name": "Sleep", "description": "Go to bed early"}
    ]
    yield

def test_index():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello world"}

def test_get_todos():
    response = client.get("/todos")
    assert response.status_code == 200
    expected = [
        {"id": 1, "name": "Sport", "description": "GO  to gym"},
        {"id": 2, "name": "Study", "description": "Read a book"},
        {"id": 3, "name": "Sleep", "description": "Go to bed early"}
    ]
    assert response.json() == expected

def test_get_todo_existing():
    response = client.get("/todos/1")
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "Sport", "description": "GO  to gym"}

def test_get_todo_not_found():
    response = client.get("/todos/999")
    assert response.status_code == 200
    assert response.json() == {"message": "Todo not found"}

def test_get_todo_invalid_id():
    response = client.get("/todos/abc")
    assert response.status_code == 422  # Unprocessable Entity for invalid int

def test_create_todo():
    new_todo = {"id": 4, "name": "Eat", "description": "Have lunch"}
    response = client.post("/todos", json=new_todo)
    assert response.status_code == 200
    assert response.json() == {"message": "Todo created successfully"}
    # Verify it was added
    response = client.get("/todos")
    assert new_todo in response.json()


def test_update_todo_existing():
    updated_todo = {"id": 1, "name": "Exercise", "description": "Go to gym"}
    response = client.put("/todos/1", json=updated_todo)
    assert response.status_code == 200
    assert response.json() == {"message": "Todo updated successfully"}
    # Verify update
    response = client.get("/todos/1")
    assert response.json() == updated_todo

def test_update_todo_not_found():
    updated_todo = {"id": 999, "name": "Test", "description": "Test"}
    response = client.put("/todos/999", json=updated_todo)
    assert response.status_code == 200
    assert response.json() == {"message": "Todo not found"}

def test_update_todo_invalid_id():
    updated_todo = {"id": 1, "name": "Test"}
    response = client.put("/todos/abc", json=updated_todo)
    assert response.status_code == 422

def test_update_todo_partial_update():
    updated_todo = {"id": 2, "name": "Learn", "description": "Read a book"}  # Same as original but different name
    response = client.put("/todos/2", json=updated_todo)
    assert response.status_code == 200
    assert response.json() == {"message": "Todo updated successfully"}
    response = client.get("/todos/2")
    assert response.json() == updated_todo