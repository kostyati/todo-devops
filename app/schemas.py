from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


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
