from fastapi import FastAPI, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.auth import create_access_token, get_current_user, hash_password, verify_password
from app.models import User
from app.repository import TodoRepository
from app.schemas import TodoCreate, TodoResponse, TodoUpdate, Token, UserCreate
from app.storage import get_db


app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")


# --- Auth endpoints ---

@app.post("/auth/register", status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    db.add(User(username=user.username, hashed_password=hash_password(user.password)))
    db.commit()
    return {"message": "User created"}


@app.post("/auth/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


# --- Todo endpoints (protected) ---

@app.get("/")
def index():
    return {"message": "Hello world"}


@app.get("/todos", response_model=list[TodoResponse])
def get_todos(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return TodoRepository(db).get_all()


@app.get("/todos/{id}", response_model=TodoResponse)
def get_todo(id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    todo = TodoRepository(db).get_by_id(id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@app.post("/todos", response_model=TodoResponse, status_code=201)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return TodoRepository(db).create(todo.name, todo.description)


@app.put("/todos/{id}", response_model=TodoResponse)
def update_todo(id: int, todo: TodoUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    repo = TodoRepository(db)
    db_todo = repo.get_by_id(id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return repo.update(db_todo, todo.name, todo.description)


@app.delete("/todos/{id}", status_code=204)
def delete_todo(id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    repo = TodoRepository(db)
    db_todo = repo.get_by_id(id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    repo.delete(db_todo)
    return Response(status_code=204)
