# DRF Library Service

**DRF Library Service** is a web application for managing a library, built with Django and Django REST Framework. The project includes a REST API, Telegram bot integration, Stripe for test payments, and Celery with Redis for background tasks.

---

## 🚀 Features
- CRUD for books and users via API
- Telegram bot for notifications
- Test payments using Stripe
- Background tasks with Celery and Redis
- Fully dockerized for easy setup

---

## 🛠 Tech Stack
- Python 3.12
- Django 5
- Django REST Framework
- PostgreSQL 15
- Redis 7
- Celery
- Docker & Docker Compose
- Telegram Bot API
- Stripe API (test mode)

---

## 📦 Installation & Run

### 1. Clone the project
```bash
git clone https://github.com/UrbanAstronaut88/drf-library-service.git
cd drf-library-service
```
### 2. Create .env from .env.sample
```bash
cp .env.sample .env
```

### 3. Run using Docker
```bash
docker compose up --build
```
This will start containers:
* db - PostgreSQL
* redis_service - Redis
* web - Django app
* telegram-bot - Bot for notifications

### Usage
* Django server: http://127.0.0.1:8000/
* API Documentation (Swagger): http://127.0.0.1:8000/api/docs/
* Telegram bot: send /start to your bot to activate
* Celery executes background tasks and notifications (if enabled)

### Management Commands
* Create Django superuser:
```bash
docker compose exec web python manage.py createsuperuser 
```
* Apply migrations:
```bash
docker compose exec web python manage.py migrate 
```
* Stop and remove containers:
```bash
docker compose down
```
* Run tests:
```bash
docker compose exec web python manage.py test borrowings
docker compose exec web python manage.py test books
docker compose exec web python manage.py test users
docker compose exec web python manage.py test payments
```
