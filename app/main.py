from fastapi import FastAPI

pseudo_db=[
    {"id":1, "name":"Sport", "description":"GO  to gym"},
    {"id":2, "name":"Study", "description":"Read a book"},
    {"id":3, "name":"Sleep", "description":"Go to bed early"}
]


app=FastAPI()

@app.get("/")
def index():
    return {"message":"Hello world"}

@app.get("/todos")
def get_todos():
    return pseudo_db

@app.get("/todos/{id}")
def get_todo(id:int):
    for todo in pseudo_db:
        if todo["id"]==id:
            return todo
    return {"message":"Todo not found"}

@app.post("/todos")
def create_todo(todo:dict):
    pseudo_db.append(todo)
    return {"message":"Todo created successfully"}  

@app.put("/todos/{id}")
def update_todo(id:int, todo:dict):
    for index, item in enumerate(pseudo_db):
        if item["id"]==id:
            pseudo_db[index]=todo
            return {"message":"Todo updated successfully"}
    return {"message":"Todo not found"}