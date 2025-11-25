from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

# we use a temporary mini-app just for demo
app = FastAPI()

class Item(BaseModel):
    id: int
    name: str

items_db = {}

@app.post("/items")
def create_item(item: Item):
    items_db[item.id] = item
    return item

@app.get("/items/{item_id}")
def get_item(item_id: int):
    return items_db.get(item_id)

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    items_db[item_id] = item
    return item

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    if item_id in items_db:
        del items_db[item_id]
        return {"message": "deleted"}
    return {"message": "not found"}

client = TestClient(app)

def test_crud_flow():
    # CREATE
    response = client.post("/items", json={"id": 1, "name": "Wizard Hat"})
    assert response.status_code == 200
    assert response.json()["name"] == "Wizard Hat"

    # READ
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Wizard Hat"

    # UPDATE
    response = client.put("/items/1", json={"id": 1, "name": "Magic Wand"})
    assert response.status_code == 200
    assert response.json()["name"] == "Magic Wand"

    # DELETE
    response = client.delete("/items/1")
    assert response.status_code == 200
    assert response.json()["message"] == "deleted"
