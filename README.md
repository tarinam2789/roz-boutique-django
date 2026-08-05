# Roz Boutique — Full-Stack E-Commerce Platform

A complete e-commerce web application built with **Python (Django)**, for a South
Asian fashion brand selling to customers in the US, Canada, and UK. Built end-to-end:
customer storefront, order/cart/wishlist system, and a fully custom admin console for
running the business day-to-day.

**Live demo:** _add your deployed URL here once live_


## Features

**Storefront**
- Homepage with dynamic sections (new arrivals, best sellers, featured/seasonal
  collections, customer reviews, newsletter signup)
- 10 product categories, each with its own browsable page
- Product pages with multi-photo/video galleries, color swatches, size selection
  with live inventory tracking, and a per-product size guide (Chest/Waist/Length/
  Sleeve/Trouser Length)
- Site-wide search, wishlist, and cart with persistent sessions
- Customer accounts: registration, login, order history, and a return-request
  workflow with a configurable return window
- Contact form with automated email notifications

**Admin console**
- Full product management: multi-image/video upload, per-size inventory, color
  tagging, category assignment, and size-guide charts — all through Django's admin,
  extended with custom inline editors
- Shipping-rule configuration by country with free-shipping thresholds
- Return-policy configuration and return-request approval workflow
- Contact-message inbox

## Tech stack

**Backend:** Python, Django, Django ORM, SQLite
**Frontend:** Jinja2 templating, vanilla JavaScript, CSS (no framework)
**Other:** Gunicorn (production server), WhiteNoise (static file serving),
python-dotenv (environment-based configuration)

## Architecture notes

- Django's ORM models the full relational schema (16+ tables: products, orders,
  categories, size guides, shipping rules, returns, etc.) with proper foreign keys,
  inline admin editors, and Django signals to keep derived data (like a product's
  cover photo) automatically in sync with its photo gallery.
- Templating uses Jinja2 (via Django's pluggable template backend) rather than
  Django's default template language, bridged with custom context processors and
  template globals for a Flask-like `url_for()`-style routing API.
- Secrets (Django secret key, email credentials) are loaded from environment
  variables via `python-dotenv` — never hardcoded, never committed.
- Deployed on Render with Gunicorn + WhiteNoise for static/media file serving.

## Local setup

```bash
git clone <your-repo-url>
cd roz-boutique-django
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# then edit .env with a real secret key and (optionally) email credentials

python3 manage.py migrate
python3 manage.py seed_data
python3 manage.py runserver
```

Visit `http://127.0.0.1:8000` for the storefront, and `http://127.0.0.1:8000/admin`
for the admin console.

## Environment variables

| Variable | Required | Purpose |
|---|---|---|
| `FLASK_SECRET_KEY` | Yes | Django's session/security secret key |
| `SMTP_USERNAME` | No | Gmail address for contact-form email notifications |
| `SMTP_PASSWORD` | No | Gmail App Password (not your regular password) |
| `DJANGO_DEBUG` | No | Set to `False` in production |
| `ALLOWED_HOSTS` | Production | Comma-separated list of allowed domains |
| `CSRF_TRUSTED_ORIGINS` | Production | Comma-separated list of trusted origins (with `https://`) |

## Known limitations

- Checkout creates real orders but isn't yet connected to a payment processor
  (Stripe integration planned).
- SQLite is used for simplicity; a larger-scale deployment would move to Postgres.

## Project structure

