# School Inventory and Cashier System

Simple full-stack Django project for inventory management, cashier checkout, and printable receipts.

## Features

- Inventory CRUD with stock validation
- Session-based cashier cart
- Checkout flow that deducts stock and stores transactions
- JSON API for inventory items, transactions, and direct checkout
- Printable receipt page
- Search, alerts, low-stock warnings, and Django admin support
- Optional login/logout flow using Django auth

## Quick Start

1. Create and activate a virtual environment.
2. Install dependencies:
   `pip install -r requirements.txt`
3. Run migrations:
   `python manage.py migrate`
4. Create an admin user:
   `python manage.py createsuperuser`
5. Start the server:
   `python manage.py runserver`

Log in at `/accounts/login/` or `/admin/`.

## Open on Any Computer or Mobile Phone

Make sure the main computer and the other computer/phone are connected to the
same Wi-Fi network or LAN.

1. Start Django for network access:
   `start-network.bat`
2. On the other device, open:
   `http://<your-computer-ip>:8000/`

Example:

```text
http://192.168.1.25:8000/
```

You can also run the command manually:

```powershell
python manage.py runserver 0.0.0.0:8000
```

If port `8000` is already busy, use another port:

```powershell
start-network.bat 8001
```

Then open:

```text
http://<your-computer-ip>:8001/
```

If the page does not open from another device, allow Python through Windows
Firewall for private networks.

Always use `http://` for the local Django server. The development server does
not provide HTTPS, so `https://...` will show an SSL protocol error.

The app includes mobile layout support plus install metadata, so supported
phones can add it to the home screen from the browser menu.

## JSON API

API routes use Django session authentication, so log in first and include the
normal CSRF token for unsafe methods such as `POST`, `PATCH`, and `DELETE`.

```text
GET    /api/items/
GET    /api/items/?q=pencil
POST   /api/items/
GET    /api/items/<id>/
PATCH  /api/items/<id>/
DELETE /api/items/<id>/
GET    /api/transactions/
POST   /api/checkout/
```

Create or update item JSON:

```json
{
  "name": "Notebook",
  "description": "80 leaves",
  "price": "35.00",
  "quantity": 20
}
```

Direct checkout JSON:

```json
{
  "items": [
    {"item_id": 1, "quantity": 2},
    {"item_id": 3, "quantity": 1}
  ]
}
```

## Deployment

This project is ready for a standard Python/Django host such as Render, Railway,
Fly.io, Heroku-style platforms, or a VPS.

### Render Blueprint

The `render.yaml` file can deploy this app as a Render Blueprint. Render will
create a PostgreSQL database, generate a secure `SECRET_KEY`, install
dependencies, collect static files, run migrations, and start the app with
Gunicorn.

Recommended production environment variables:

```text
DEBUG=False
SECRET_KEY=<a long random secret>
ALLOWED_HOSTS=<your-domain.example.com>
CSRF_TRUSTED_ORIGINS=https://<your-domain.example.com>
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

If your host provides PostgreSQL, set `DATABASE_URL` to the database connection
string. If `DATABASE_URL` is not set, the app uses the local SQLite database.

### Vercel

This repo includes `api/index.py` and `vercel.json` so Vercel can route all
requests into the Django WSGI app.

For Vercel production, set these environment variables in Project Settings:

```text
DEBUG=False
SECRET_KEY=<a long random secret>
DATABASE_URL=<your hosted PostgreSQL connection string>
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

Use a hosted PostgreSQL database such as Vercel Postgres, Neon, Supabase, or
Render PostgreSQL. Do not rely on the local `db.sqlite3` file on Vercel:
serverless deployments cannot persist normal database writes there, so login,
checkout, admin changes, and branch creation can fail with server errors.

Build command:

```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
```

Windows PowerShell:

```powershell
python -m pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
```

Start command:

```bash
gunicorn school_inventory.wsgi:application
```

Generate a production secret key with:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
