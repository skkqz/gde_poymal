# gde_poymal — сообщество рыбаков

API для приложения «Где поймал?» — пользователи, точки лова. `Django 6.1` + `DRF` + `PostgreSQL` + `JWT`.

Скачать: `https://github.com/skkqz/gde_poymal.git`

---

## Требования
`Python 3.13` · `PostgreSQL 16` · `uv` (или `pip`) · `Git`

---

## Как скачать

```bash
git clone https://github.com/skkqz/gde_poymal.git
cd gde_poymal
```

---

## Как установить

**Windows (PowerShell):**
```powershell
uv sync --group dev
Copy-Item .env.example .env
```

**Linux / macOS:**
```bash
uv sync --group dev
cp .env.example .env
```

Открой `.env` и заполни `SECRET_KEY` и `DATABASE_URL`:
```env
DEBUG=True
SECRET_KEY=django-insecure-замени
DATABASE_URL=postgresql://user:password@localhost:5432/db_name
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## Как создать БД

**Windows:**
```powershell
psql -U postgres -c "CREATE USER app_user WITH PASSWORD 'password';"
psql -U postgres -c "CREATE DATABASE app_db OWNER app_user;"
```

**Linux:**
```bash
sudo -u postgres psql -c "CREATE USER app_user WITH PASSWORD 'password';"
sudo -u postgres psql -c "CREATE DATABASE app_db OWNER app_user;"
```

---

## Как запустить

**Windows:**
```powershell
uv run python manage.py migrate
uv run python manage.py createsuperuser  # логин — email
uv run python manage.py runserver
```

**Linux / macOS:**
```bash
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

Открой:
* `http://127.0.0.1:8000/admin/` — админка
* `http://127.0.0.1:8000/api/docs/` — Swagger (только при `DEBUG=True`)

---

## Автор

skkq — [github.com/skkqz](https://github.com/skkqz) · skkqw@yandex.ru
