# ServiceHub

**general-purpose plan and request manager** built with Django. Administrators publish plans (subscriptions, licences, memberships, service packages...), customers request them in one click, and every approval, rejection and support question is tracked in one place

![Brand comparison](docs/screenshots/00-brand-comparison.png)

---

## Features

**Staff (any user with `is_staff`)**
- Dashboard with totals: customers, categories, items, requests (pending / approved / rejected) and open tickets
- Create, edit and delete categories and items (price, duration, active/hidden)
- Review requests, filter by status, approve or reject with one click
- List and remove customer accounts
- Answer customer support tickets

**Customers**
- Self-service sign-up (no admin approval needed); optional phone and location
- Browse the catalogue, filter by category, send a request
- Duplicate protection: a second pending request for the same item is blocked
- Follow request status and ask questions from their own dashboard

**Platform**
- Brand presets driven by data (colours, wording, copy, demo catalogue)
- Live theme preview in development with `?brand=google`
- No JavaScript framework and no CDN: one stylesheet, works offline
- Secure defaults: POST-only state changes, CSRF on every form, role checks on every staff view, secrets from environment variables
- Contact form that prints to the console in development and uses SMTP when configured

---

## Screenshots

### Public pages

| Generic | Tesla |
|---|---|
| ![Generic home](docs/screenshots/generic-home.png) | ![Tesla home](docs/screenshots/tesla-home.png) |

| Google | Microsoft |
|---|---|
| ![Google home](docs/screenshots/google-home.png) | ![Microsoft home](docs/screenshots/microsoft-home.png) |

| Spotify | Login |
|---|---|
| ![Spotify home](docs/screenshots/spotify-home.png) | ![Login](docs/screenshots/generic-login.png) |

### Staff area

**Dashboard (Tesla theme, "Reservations")**

![Tesla staff dashboard](docs/screenshots/tesla-staff-dashboard.png)

**Dashboard (Google theme, "Subscriptions")**

![Google staff dashboard](docs/screenshots/google-staff-dashboard.png)

**Approving requests**

![Google staff requests](docs/screenshots/google-staff-requests.png)

**Managing the catalogue**

![Tesla staff catalogue](docs/screenshots/tesla-staff-catalog.png)

**Customers and support tickets**

| Customers | Tickets |
|---|---|
| ![Customers](docs/screenshots/google-staff-customers.png) | ![Tickets](docs/screenshots/google-staff-tickets.png) |

**Adding an item**

![New item form](docs/screenshots/google-form-new-item.png)

### Customer area

**Browsing (Spotify, Tesla, Google themes)**

![Spotify browse](docs/screenshots/spotify-customer-browse.png)

| Tesla | Google |
|---|---|
| ![Tesla browse](docs/screenshots/tesla-customer-browse.png) | ![Google browse](docs/screenshots/google-customer-browse.png) |

**Dashboard and request history (Microsoft theme)**

| Dashboard | My requests |
|---|---|
| ![Customer dashboard](docs/screenshots/microsoft-customer-dashboard.png) | ![My requests](docs/screenshots/microsoft-customer-requests.png) |

---

## Quick start

Requirements: Python 3.9+ (Django 4.2 or newer, see `requirements.txt`).

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env                 # optional; defaults work for local development
export BRAND=tesla                   # optional; see Brand presets

python manage.py makemigrations accounts catalog
python manage.py migrate
python manage.py seed_demo --brand tesla
python manage.py runserver
```
---

## Brand presets

Set `BRAND` to one of `generic`, `tesla`, `google`, `microsoft`, `spotify`.

| Brand | Item called | Request called | Action button | Category called |
|---|---|---|---|---|
| generic | Plan | Request | Request this plan | Category |
| tesla | Service plan | Reservation | Reserve this plan | Product line |
| google | Subscription | Subscription request | Subscribe | Product |
| microsoft | Licence | Licence request | Request licence | Suite |
| spotify | Membership | Join request | Join now | Tier |

## How it works

### Data model

```
User (Django auth) --1:1-- Profile(phone, location)       accounts
User --< ServiceRequest >-- Offering >-- Category         catalog
User --< SupportTicket(subject, message, response)        catalog
```

| Model | Key fields |
|---|---|
| `Category` | name (unique), description |
| `Offering` | category, name, description, price, duration_months, is_active |
| `ServiceRequest` | customer, offering, status (`pending` / `approved` / `rejected`) |
| `SupportTicket` | customer, subject, message, response, status (`open` / `answered`) |
| `Profile` | user, phone (optional), location (optional) |

### Request lifecycle

1. A customer clicks the action button on an item, which sends a POST to create a `pending` request.
2. If the same customer already has a pending request for that item, no duplicate is created and a message is shown.
3. Staff open **Requests**, filter if needed, and approve or reject (POST only).
4. The customer sees the new status in **My requests** and on their dashboard.

### Roles

| Role | How it is decided | Access |
|---|---|---|
| Visitor | not logged in | public pages, login, sign-up |
| Customer | logged in, `is_staff = False` | browse, request, own requests and tickets |
| Staff | `is_staff = True` | everything under the staff area |

Staff views use `StaffRequiredMixin`: anonymous users are redirected to login, other users get HTTP 403

---

## URL map

| Path | Name | Who |
|---|---|---|
| `/` | `core:home` | everyone |
| `/about/`, `/contact/` | `core:about`, `core:contact` | everyone |
| `/accounts/login/`, `/accounts/logout/`, `/accounts/signup/` | `accounts:*` | everyone |
| `/app/` | `catalog:dashboard` | logged in (staff or customer view) |
| `/app/browse/`, `/app/browse/<id>/request/` | `browse`, `create-request` | logged in |
| `/app/my-requests/`, `/app/my-tickets/`, `/app/my-tickets/new/` | customer pages | logged in |
| `/app/categories/` (+ `new`, `<id>/edit`, `<id>/delete`) | category CRUD | staff |
| `/app/items/` (+ `new`, `<id>/edit`, `<id>/delete`) | item CRUD | staff |
| `/app/requests/`, `/app/requests/<id>/approve/` or `/reject/` | review | staff |
| `/app/customers/`, `/app/customers/<id>/delete/` | customers | staff |
| `/app/tickets/`, `/app/tickets/<id>/respond/` | support | staff |
| `/django-admin/` | Django admin site | superusers |

---

## Project layout

```
servicehub/
├── manage.py
├── requirements.txt
├── .env.example
├── config/                 settings (env-driven), urls, wsgi, asgi
├── core/
│   ├── brands.py           brand presets (edit this to rebrand)
│   ├── context_processors.py   injects brand, wording, currency
│   ├── middleware.py       ?brand= preview switch (DEBUG only)
│   ├── views.py / forms.py home, about, contact
│   ├── management/commands/seed_demo.py
│   └── tests.py
├── accounts/               sign-up, login/logout, Profile
├── catalog/                models, forms, views, urls, admin
├── templates/              base, app shell, core/, accounts/, catalog/
├── static/css/app.css      single stylesheet, brand colours via CSS variables
├── tools/render_previews.py    screenshots without running Django
└── docs/screenshots/       images used in this README
```

---
