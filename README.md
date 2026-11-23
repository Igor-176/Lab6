\# Лабораторная работа 6: Введение в FastAPI



Описание проекта:

В ходе лабораторной работы было разработано API для управления товарами на фреймворке FastAPI. Проект развивался поэтапно: от простого файла main.py до структурированного приложения с роутерами, конфигурацией и логированием.



=== ЗАДАНИЕ 1: ПОДГОТОВИТЕЛЬНЫЙ ЭТАП ===

Что сделано: Инициализирован проект с помощью uv, создано виртуальное окружение, установлены fastapi и uvicorn. Создано базовое приложение с корневым маршрутом.



Код main.py на этом этапе:

from fastapi import FastAPI



app = FastAPI()



@app.get("/")

def read\_root():

&#x20;   return {"message": "Hello, FastAPI!"}



=== ЗАДАНИЕ 2: ПАРАМЕТРЫ ПУТИ И QUERY ===

Что сделано: Добавлен эндпоинт /items/{item\_id}, принимающий обязательный целочисленный параметр пути и необязательный query-параметр q.



Добавленный код:

@app.get("/items/{item\_id}")

def read\_item(item\_id: int, q: str | None = None):

&#x20;   return {"item\_id": item\_id, "q": q}



=== ЗАДАНИЕ 3: МОДЕЛЬ PYDANTIC И POST-ЗАПРОС ===

Что сделано: Библиотека pydantic добавлена в явные зависимости. Создана модель Item для валидации данных и добавлен POST-эндпоинт для создания товара.



Добавленный код:

from pydantic import BaseModel



class Item(BaseModel):

&#x20;   name: str

&#x20;   price: float

&#x20;   is\_offer: bool | None = None



@app.post("/items/", response\_model=Item)

def create\_item(item: Item):

&#x20;   return item



=== ЗАДАНИЕ 4: ОРГАНИЗАЦИЯ КОДА (РЕФАКТОРИНГ) ===

Что сделано: Код разбит на модули. Создана директория app/ с пакетами. Эндпоинты товаров вынесены в отдельный роутер с префиксом /items.



Код app/routers/items.py:

from fastapi import APIRouter

from pydantic import BaseModel



router = APIRouter(prefix="/items", tags=\["items"])



class Item(BaseModel):

&#x20;   name: str

&#x20;   price: float

&#x20;   is\_offer: bool | None = None



@router.get("/{item\_id}")

def read\_item(item\_id: int, q: str | None = None):

&#x20;   return {"item\_id": item\_id, "q": q}



@router.post("/")

def create\_item(item: Item):

&#x20;   return item



Обновленный main.py:

from fastapi import FastAPI

from app.routers import items



app = FastAPI()



app.include\_router(items.router)



@app.get("/")

def read\_root():

&#x20;   return {"message": "Hello, FastAPI!"}



=== ЗАДАНИЕ 5: КОНФИГУРАЦИЯ ЧЕРЕЗ PYDANTIC SETTINGS ===

Что сделано: Установлен pydantic-settings. Создан класс Settings для чтения переменных окружения из файла .env. Название приложения и данные администратора теперь берутся из конфига.



Код app/config.py:

from pydantic\_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):

&#x20;   app\_name: str = "My FastAPI Lab"

&#x20;   admin\_email: str

&#x20;   items\_per\_page: int = 10

&#x20;   

&#x20;   model\_config = SettingsConfigDict(env\_file=".env")



Добавлено в main.py:

from app.config import Settings



settings = Settings()

app = FastAPI(title=settings.app\_name)



@app.get("/info")

def get\_info():

&#x20;   return {

&#x20;       "app\_name": settings.app\_name,

&#x20;       "admin\_email": settings.admin\_email,

&#x20;       "items\_per\_page": settings.items\_per\_page

&#x20;   }



=== ЗАДАНИЕ 6, 7, 8: ОБРАБОТКА ОШИБОК, PUT, ЛОГИРОВАНИЕ ===

Что сделано: 

1\. Добавлена имитация БД (fake\_db). Ошибка 404 при отсутствии товара.

2\. Добавлены описания параметров (Path, Query, Field) и метаданные приложения.

3\. Добавлен PUT-эндпоинт для обновления товара с проверкой уникальности имени.

4\. Подключено логирование (INFO, WARNING, ERROR) в отдельном файле.



Итоговый код app/logger.py:

import logging

import sys



logger = logging.getLogger("my\_app\_logger")

logger.setLevel(logging.INFO)



handler = logging.StreamHandler(sys.stdout)



formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

handler.setFormatter(formatter)



logger.addHandler(handler)



Итоговый код app/routers/items.py (включает всё из заданий 6, 7, 8):

from fastapi import APIRouter, HTTPException, Path, Query

from pydantic import BaseModel, Field

from app.logger import logger



router = APIRouter(prefix="/items", tags=\["items"])



class Item(BaseModel):

&#x20;   name: str = Field(..., title="Название", example="Телефон")

&#x20;   price: float = Field(..., gt=0, title="Цена", example=199.99)

&#x20;   is\_offer: bool | None = Field(None, title="Акционный товар")



fake\_db = {1: {"name": "Foo", "price": 50.2, "is\_offer": False}}



@router.get("/{item\_id}")

def read\_item(

&#x20;   item\_id: int = Path(..., title="ID товара", ge=1),

&#x20;   q: str | None = Query(None, title="Поисковый запрос", max\_length=50)

):

&#x20;   logger.info(f"Запрос на получение товара с ID: {item\_id}, поисковый запрос: {q}")

&#x20;   if item\_id not in fake\_db:

&#x20;       logger.warning(f"Товар с ID {item\_id} не найден")

&#x20;       raise HTTPException(status\_code=404, detail="Item not found")

&#x20;   return {"item\_id": item\_id, "item": fake\_db\[item\_id], "q": q}



@router.post("/", response\_model=Item)

def create\_item(item: Item):

&#x20;   logger.info(f"Попытка создания товара: {item.name}")

&#x20;   for existing\_item in fake\_db.values():

&#x20;       if existing\_item\["name"] == item.name:

&#x20;           logger.error(f"Ошибка: Товар с именем '{item.name}' уже существует")

&#x20;           raise HTTPException(status\_code=400, detail="Item with this name already exists")

&#x20;   

&#x20;   new\_id = max(fake\_db.keys()) + 1 if fake\_db else 1

&#x20;   fake\_db\[new\_id] = item.model\_dump()

&#x20;   logger.info(f"Товар '{item.name}' успешно создан с ID {new\_id}")

&#x20;   return item



@router.put("/{item\_id}", response\_model=Item)

def update\_item(

&#x20;   item\_id: int = Path(..., title="ID товара", ge=1),

&#x20;   item: Item = None

):

&#x20;   logger.info(f"Попытка обновления товара с ID: {item\_id}")

&#x20;   if item\_id not in fake\_db:

&#x20;       logger.warning(f"Ошибка обновления: Товар с ID {item\_id} не найден")

&#x20;       raise HTTPException(status\_code=404, detail="Item not found")

&#x20;   

&#x20;   for existing\_id, existing\_item in fake\_db.items():

&#x20;       if existing\_id != item\_id and existing\_item\["name"] == item.name:

&#x20;           logger.error(f"Ошибка: Имя '{item.name}' уже занято другим товаром")

&#x20;           raise HTTPException(status\_code=400, detail="Item with this name already exists")



&#x20;   fake\_db\[item\_id] = item.model\_dump()

&#x20;   logger.info(f"Товар с ID {item\_id} успешно обновлен")

&#x20;   return item



Итоговый код main.py:

from fastapi import FastAPI

from app.routers import items

from app.config import Settings



settings = Settings()



app = FastAPI(

&#x20;   title=settings.app\_name,

&#x20;   description="Лабораторная работа по FastAPI",

&#x20;   version="1.0.0",

&#x20;   contact={

&#x20;       "name": "Студент",

&#x20;       "email": settings.admin\_email,

&#x20;   }

)



app.include\_router(items.router)



@app.get("/")

def read\_root():

&#x20;   return {"message": "Hello, FastAPI!"}



@app.get("/info")

def get\_info():

&#x20;   return {

&#x20;       "app\_name": settings.app\_name,

&#x20;       "admin\_email": settings.admin\_email,

&#x20;       "items\_per\_page": settings.items\_per\_page

&#x20;   }

