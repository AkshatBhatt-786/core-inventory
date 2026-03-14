# CoreInventory — Inventory Management System

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Django](https://img.shields.io/badge/Django-5.x-green)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey)
![License](https://img.shields.io/badge/License-MIT-yellow)

> A modular Inventory Management System built with Django — digitizing stock operations including receipts, deliveries, internal transfers, and adjustments with real-time tracking.

---

## What is CoreInventory?

CoreInventory replaces manual registers, Excel sheets, and scattered tracking methods with a centralized, real-time, easy-to-use web application. It is designed for inventory managers and warehouse staff who need to track stock movement across multiple warehouses and locations.

---

## Key Features

- **Authentication** — Secure login, signup with input validation
- **Dashboard** — Real-time KPIs: total products, low stock alerts, pending receipts and deliveries
- **Product Management** — Create and manage products with SKU, category, unit of measure, and reorder rules
- **Receipts** — Record incoming stock from vendors; auto-increases product stock on validation
- **Delivery Orders** — Record outgoing stock for customer shipments; auto-decreases stock on validation
- **Stock Adjustments** — Fix mismatches between recorded and physical stock counts
- **Move History / Stock Ledger** — Full audit trail of every stock movement with IN/OUT color coding
- **Multi-warehouse Support** — Manage multiple warehouses and locations
- **Low Stock Alerts** — Automatic alerts when stock falls below reorder threshold

---

## Tech Stack

| Layer       | Technology          |
|-------------|---------------------|
| Backend     | Python 3.12, Django 5.x |
| Database    | SQLite (local)      |
| Frontend    | Django Templates, Tailwind CSS (CDN) |
| Auth        | Django built-in auth |
| Config      | python-decouple (.env) |
| Version Control | Git + GitHub   |

---

## Project Structure

```
core-inventory/
├── apps/
│   ├── accounts/       # Login, signup, authentication
│   ├── dashboard/      # Landing page, KPI widgets
│   ├── products/       # Product & category management
│   ├── operations/     # Receipts, deliveries, adjustments
│   └── ledger/         # Stock movement history (read-only log)
├── templates/          # Global base templates + partials
├── static/             # CSS, JS, images
├── docs/               # Project documentation
├── coreinventory/      # Django project settings
├── .env.example        # Environment variable template
├── requirements.txt    # Python dependencies
└── manage.py
```

---

## Team

Built for the **Odoo x Indus Hackathon** by:

| Name | Role |
|------|------|
| Aksha Bhatt | Backend — Models, Views, Business Logic |
| Maharshi Nimbark | Frontend — Templates, UI, Dashboard |

---

## Quick Start

See [SETUP.md](SETUP.md) for full installation instructions.

```bash
git clone https://github.com/AkshatBhatt-786/core-inventory.git
cd core-inventory
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
cp .env.example .env         # Fill in your SECRET_KEY
python manage.py migrate
python manage.py runserver
```

---

## Documentation

| File | Description |
|------|-------------|
| [SETUP.md](SETUP.md) | Local installation and running guide |
| [MODELS.md](MODELS.md) | Database schema and model relationships |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Git workflow and contribution guide |

---

## License

This project is licensed under the MIT License.