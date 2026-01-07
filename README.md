# Разработка REST API и работа с OpenAPI
## Яблонская Евгения, ИВТ-1.2

Результат:
<img width="1820" height="972" alt="image" src="https://github.com/user-attachments/assets/4447a6ab-7fc8-433f-abae-28fcbfa2f923" />

<img width="1816" height="948" alt="image" src="https://github.com/user-attachments/assets/7580df39-6455-4f31-bb2c-28bf229f09f8" />

<img width="1803" height="225" alt="image" src="https://github.com/user-attachments/assets/a14ef1d2-3c94-4dfc-a111-12c8403d46e2" />

# Books API

REST‑сервис для управления библиотекой книг на базе FastAPI.

## Функциональность

- Получение списка книг (с фильтрацией по автору, году; пагинацией).
- Получение книги по ID.
- Создание, обновление (полное и частичное), удаление книг.
- Статистика по книгам (количество, распределение по авторам и векам).
- Валидация данных (Pydantic).
- Аутентификация через API‑ключ.
- Автоматическая документация (Swagger UI, ReDoc).
- Хранение данных в SQLite (SQLAlchemy).

## Требования

- Python 3.8+
- pip

## Установка и запуск

1. Создайте и активируйте виртуальное окружение:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/MacOS
   source venv/bin/activate
   ```

2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

3. Запустите сервер:
   ```bash
   uvicorn main:app --reload
   ```

## Доступ к сервису

- **API:** `http://localhost:8000`
- **Swagger UI (документация):** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI JSON:** `http://localhost:8000/openapi.json`

## Тестирование

Примеры запросов доступны в Swagger UI (`/docs`). Для операций создания, обновления и удаления требуется заголовок:
```
X-API-Key: secret-api-key-12345
```

## Структура проекта

- `main.py` — основное приложение FastAPI.
- `database.py` — настройка SQLite и SQLAlchemy.
- `auth.py` — логика аутентификации.
- `requirements.txt` — зависимости.
- `books.db` — база данных (создаётся автоматически).

## Примечания

- API‑ключ задан в `auth.py` (в проде используйте переменные окружения).
- База данных `books.db` создаётся при первом запуске.
- Для просмотра БД можно использовать **DB Browser for SQLite**.
