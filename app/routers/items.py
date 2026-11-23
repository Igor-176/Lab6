from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel, Field
from app.logger import logger  # Импортируем наш логгер

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
    logger.info(f"Запрос на получение товара с ID: {item_id}, поисковый запрос: {q}")
    if item_id not in fake_db:
        logger.warning(f"Товар с ID {item_id} не найден")
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item_id": item_id, "item": fake_db[item_id], "q": q}

@router.post("/", response_model=Item)
def create_item(item: Item):
    logger.info(f"Попытка создания товара: {item.name}")
    for existing_item in fake_db.values():
        if existing_item["name"] == item.name:
            logger.error(f"Ошибка: Товар с именем '{item.name}' уже существует")
            raise HTTPException(status_code=400, detail="Item with this name already exists")
    
    new_id = max(fake_db.keys()) + 1 if fake_db else 1
    fake_db[new_id] = item.model_dump()
    logger.info(f"Товар '{item.name}' успешно создан с ID {new_id}")
    return item

@router.put("/{item_id}", response_model=Item)
def update_item(
    item_id: int = Path(..., title="ID товара", ge=1),
    item: Item = None
):
    logger.info(f"Попытка обновления товара с ID: {item_id}")
    if item_id not in fake_db:
        logger.warning(f"Ошибка обновления: Товар с ID {item_id} не найден")
        raise HTTPException(status_code=404, detail="Item not found")
    
    for existing_id, existing_item in fake_db.items():
        if existing_id != item_id and existing_item["name"] == item.name:
            logger.error(f"Ошибка: Имя '{item.name}' уже занято другим товаром")
            raise HTTPException(status_code=400, detail="Item with this name already exists")

    fake_db[item_id] = item.model_dump()
    logger.info(f"Товар с ID {item_id} успешно обновлен")
    return item