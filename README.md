# Video Balancer

Простой сервис-балансировщик запросов, который направляет запросы либо на CDN, либо на оригинал.

## Быстрый старт
```bash
  pip install virtualenv
```
```bash
  pip3 install poetry
```

### С Docker Compose

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd video_balancer
```

2. Запуск:
```bash
docker-compose up -d
```

3. Сервис будет доступен по адресу: http://localhost:8000

### API документация
Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc

## Использование

### Балансировка видео-запросов

Основной endpoint для балансировки:

```bash
GET /?video=http://s1.origin-cluster/video/1488/xcg2djHckad.m3u8
```

Сервис автоматически перенаправит запрос на:
- **CDN**: `http://cdn.example.com/s1/video/1488/xcg2djHckad.m3u8`
- **Origin**: `http://s1.origin-cluster/video/1488/xcg2djHckad.m3u8`

### JSON API

Для получения URL без редиректа:

```bash
POST /balance
Content-Type: application/json

{
  "video": "http://s1.origin-cluster/video/1488/xcg2djHckad.m3u8"
}
```

Ответ:
```json
{
  "redirect_url": "http://cdn.example.com/s1/video/1488/xcg2djHckad.m3u8",
  "target": "cdn"
}
```

### Управление конфигурацией

#### Получить активную конфигурацию:
```bash
GET /srv/config/
```

#### Создать новую конфигурацию:
```bash
POST /srv/config/
Content-Type: application/json

{
  "cdn_host": "cdn.example.com",
  "cdn_ratio": 8,
  "origin_ratio": 2,
  "is_active": true
}
```

#### Обновить конфигурацию:
```bash
PUT /srv/config/{config_id}
Content-Type: application/json

{
  "cdn_ratio": 7,
  "origin_ratio": 3
}
```

#### Активировать конфигурацию:
```bash
POST /srv/config/{config_id}/activate
```

### Соотношения

Соотношение CDN:Origin определяет, какой процент запросов направляется в каждую сторону:
- `cdn_ratio=9, origin_ratio=1` → 90% CDN, 10% Origin
- `cdn_ratio=5, origin_ratio=5` → 50% CDN, 50% Origin

## Мониторинг

### Health Check
```bash
GET /health
```

### Статистика балансировщика
```bash
GET /stats
```

## Разработка

### Структура проекта

```
src/
├── app/
│   ├── api/           # API endpoints
│   ├── srv/           # Сервисные endpoints
│   ├── models.py      # SQLAlchemy модели
│   ├── schemas.py     # Pydantic схемы
│   ├── crud.py        # CRUD операции
│   ├── balancer.py    # Логика балансировки
│   ├── database.py    # Настройки БД
│   └── main.py        # FastAPI приложение
├── config.py          # Конфигурация
├── logger_config.py   # Конфигурация логирования
├── logs/              # Логи приложения
└── ...
```

1. Установите зависимости:
```bash
  poetry install
```

2. Настройте переменные окружения:
```bash
  cp env.example .env
# Отредактируйте .env файл
# Все настройки можно посмотреть в config.py
```

3. Запустить PostgreSQL:
```bash
    docker run -d --name postgres \
      -e POSTGRES_DB=video_balancer \
      -e POSTGRES_USER=postgres \
      -e POSTGRES_PASSWORD=password \
      -p 5432:5432 \
      postgres:15-alpine
```

4. Запустите приложение:
```bash
  poetry run uvicorn src.app.main:app --reload
```

