from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel, Field

router = APIRouter(prefix="/items", tags=["items"])

class Item(BaseModel):
    name: str = Field(..., title="Название", example="Телефон")
    price: float = Field(..., gt=0, title="Цена", example=199.99)
    is_offer: bool | None = Field(None, title="Акционный товар")

fake_db = {1: {"name": "Foo", "price": 50.2, "is_offer": False}}

@router.get("/{item_id}")
def read_item(
    item_id: int = Path(..., title="ID товара", ge=1),
    q: str | None = Query(None, title="Поисковый запрос", max_length=50)
):
    if item_id not in fake_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item_id": item_id, "item": fake_db[item_id], "q": q}

@router.post("/", response_model=Item)
def create_item(item: Item):
    # Проверка на уникальность имени
    for existing_item in fake_db.values():
        if existing_item["name"] == item.name:
            raise HTTPException(status_code=400, detail="Item with this name already exists")
    
    # Имитация сохранения (добавляем в словарь с новым id)
    new_id = max(fake_db.keys()) + 1 if fake_db else 1
    fake_db[new_id] = item.model_dump()
    return item

@router.put("/{item_id}", response_model=Item)
def update_item(
    item_id: int = Path(..., title="ID товара", ge=1),
    item: Item = None
):
    # Проверка существования
    if item_id not in fake_db:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Проверка уникальности имени (если имя меняется, проверяем, не занято ли оно другим товаром)
    for existing_id, existing_item in fake_db.items():
        if existing_id != item_id and existing_item["name"] == item.name:
            raise HTTPException(status_code=400, detail="Item with this name already exists")

    fake_db[item_id] = item.model_dump()
    return item