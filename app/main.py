from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models import Todo
from app.storage import get_db


app = FastAPI()


# --- Schemas ---

class TodoCreate(BaseModel):
    name: str
    description: str | None = None


class TodoUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class TodoResponse(BaseModel):
    id: int
    name: str
    description: str | None

    model_config = {"from_attributes": True}


# --- Endpoints ---

@app.get("/")
def index():
    return {"message": "Hello world"}


@app.get("/todos", response_model=list[TodoResponse])
def get_todos(db: Session = Depends(get_db)):
    return db.query(Todo).all()


@app.get("/todos/{id}", response_model=TodoResponse)
def get_todo(id: int, db: Session = Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@app.post("/todos", response_model=TodoResponse, status_code=201)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = Todo(name=todo.name, description=todo.description)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo


@app.put("/todos/{id}", response_model=TodoResponse)
def update_todo(id: int, todo: TodoUpdate, db: Session = Depends(get_db)):
    db_todo = db.query(Todo).filter(Todo.id == id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if todo.name is not None:
        db_todo.name = todo.name
    if todo.description is not None:
        db_todo.description = todo.description
    db.commit()
    db.refresh(db_todo)
    return db_todo
