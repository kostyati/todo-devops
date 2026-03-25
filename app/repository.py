from sqlalchemy.orm import Session

from app.models import Todo


class TodoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Todo]:
        return self.db.query(Todo).all()

    def get_by_id(self, id: int) -> Todo | None:
        return self.db.query(Todo).filter(Todo.id == id).first()

    def create(self, name: str, description: str | None) -> Todo:
        todo = Todo(name=name, description=description)
        self.db.add(todo)
        self.db.commit()
        self.db.refresh(todo)
        return todo

    def update(self, todo: Todo, name: str | None, description: str | None) -> Todo:
        if name is not None:
            todo.name = name
        if description is not None:
            todo.description = description
        self.db.commit()
        self.db.refresh(todo)
        return todo

    def delete(self, todo: Todo) -> None:
        self.db.delete(todo)
        self.db.commit()
