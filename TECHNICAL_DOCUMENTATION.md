# Webshop Backend - Technical Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Database Design](#database-design)
5. [Setup & Installation](#setup--installation)
6. [Project Structure](#project-structure)
7. [API Documentation](#api-documentation)
8. [Django ORM Usage](#django-orm-usage)
9. [Development Workflow](#development-workflow)
10. [Deployment](#deployment)

---

## Project Overview

### Purpose
This project implements a fully functional e-commerce backend system using Django and PostgreSQL. It provides a RESTful API for managing customers, products, orders, and shopping carts.

### Goals Achieved
- ✅ Complete database schema implementation following ER diagram
- ✅ Django ORM models with full relationship mapping
- ✅ RESTful API endpoints for all entities
- ✅ Automated setup with Docker containerization
- ✅ Sample data generation for testing
- ✅ Admin interface for data management
- ✅ Production-ready structure with entrypoint automation

### Why This Approach?
- **Django ORM**: Provides database abstraction, security, and maintainability
- **Docker**: Ensures consistent environment across development and production
- **PostgreSQL**: Reliable, scalable relational database with excellent Django support
- **Automated Setup**: Reduces onboarding time from hours to minutes
- **Separation of Concerns**: Clean architecture with distinct project/app structure

---

## Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Layer                         │
│                    (Browser/API Client)                      │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST API
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Django Application                        │
│  ┌────────────────┐  ┌────────────────┐  ┌───────────────┐ │
│  │   Views/APIs   │  │     Models     │  │  Admin Panel  │ │
│  │   (shop/views) │◄─┤  (shop/models) │◄─┤  (shop/admin) │ │
│  └────────────────┘  └────────────────┘  └───────────────┘ │
│           │                   │                              │
│           └───────────────────┼──────────────────────────────┤
│                              ORM                             │
└──────────────────────────────┬──────────────────────────────┘
                               │ SQL
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    PostgreSQL Database                       │
│  ┌──────────┐ ┌─────────┐ ┌────────┐ ┌──────┐ ┌────────┐  │
│  │ Customer │ │ Product │ │  Order │ │ Cart │ │Category│  │
│  └──────────┘ └─────────┘ └────────┘ └──────┘ └────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Container Architecture

```
Docker Compose
├── db (PostgreSQL 17)
│   ├── Port: 5432
│   ├── Volume: postgres_data (persistent)
│   └── Environment: .env file
│
└── web (Django Application)
    ├── Port: 8000
    ├── Depends on: db
    ├── Entrypoint: entrypoint.sh (automation)
    └── Volume: .:/app (development hot-reload)
```

---

## Technology Stack

### Backend Framework
- **Django 5.2.8**: High-level Python web framework
  - Why: Rapid development, built-in ORM, admin interface, security features
  - Use case: API backend, data modeling, business logic

### Database
- **PostgreSQL 17**: Advanced open-source relational database
  - Why: ACID compliance, robust relationships, JSON support, excellent Django integration
  - Use case: Primary data store for all entities

### Containerization
- **Docker**: Container platform
  - Why: Consistency, isolation, easy deployment
- **Docker Compose**: Multi-container orchestration
  - Why: Simple local development setup, service dependency management

### Package Management
- **UV**: Modern, fast Python package installer and resolver
  - Why: 10-100x faster than pip, better dependency resolution, built in Rust
  - Use case: Package installation, virtual environment management

### Python Packages
```txt
Django==5.2.8          # Web framework
psycopg2-binary        # PostgreSQL adapter
gunicorn               # WSGI HTTP server (production)
```

#### Using pyproject.toml (Modern Approach)
The project uses `pyproject.toml` for dependency management following PEP 621:
```toml
[project]
name = "webshop-backend"
version = "1.0.0"
requires-python = ">=3.13"
dependencies = [
    "django>=5.2.8",
    "psycopg2-binary>=2.9.9",
    "gunicorn>=22.0.0",
]
```

---

## Database Design

### Entity Relationship Diagram

The database follows a normalized relational design based on the provided ER diagram:

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   CUSTOMER   │────────▶│    ORDER     │────────▶│  ORDER_ITEM  │
│              │   1:n   │              │   1:n   │              │
│ customer_id  │         │ order_id     │         │order_item_id │
│ first_name   │         │ customer_id  │         │ order_id     │
│ last_name    │         │ order_date   │         │ product_id   │
│ email        │         │ status       │         │ quantity     │
│ password     │         │ total_amount │         │price_per_unit│
│ strasse      │         └──────────────┘         └──────────────┘
│ ort          │                                          │
│ plz          │                                          │ n:1
└──────┬───────┘                                          │
       │ 1:1                                              ▼
       ▼                                          ┌──────────────┐
┌──────────────┐         ┌──────────────┐        │   PRODUCT    │
│     CART     │────────▶│  CART_ITEM   │───────▶│              │
│              │   1:n   │              │   n:1  │  product_id  │
│   cart_id    │         │ cart_item_id │        │    name      │
│ customer_id  │         │   cart_id    │        │ description  │
│last_updated  │         │  product_id  │        │    price     │
└──────────────┘         │  quantity    │        │    stock     │
                         └──────────────┘        │ category_id  │
                                                 └──────┬───────┘
                                                        │ n:1
                                                        ▼
                                                 ┌──────────────┐
                                                 │   CATEGORY   │
                                                 │              │
                                                 │ category_id  │
                                                 │category_name │
                                                 └──────────────┘
```

### Database Tables

#### CUSTOMER
- **Purpose**: Store customer account information
- **Primary Key**: `customer_id` (auto-increment)
- **Unique Constraint**: `email`
- **Relationships**: 
  - One-to-Many with ORDER
  - One-to-One with CART

#### CATEGORY
- **Purpose**: Organize products into categories
- **Primary Key**: `category_id` (auto-increment)
- **Unique Constraint**: `category_name`
- **Relationships**: One-to-Many with PRODUCT

#### PRODUCT
- **Purpose**: Store product catalog
- **Primary Key**: `product_id` (auto-increment)
- **Foreign Keys**: `category_id` → CATEGORY
- **Constraints**: `price >= 0`, `stock >= 0`
- **Indexes**: `category_id` for faster lookups

#### ORDER
- **Purpose**: Track customer orders
- **Primary Key**: `order_id` (auto-increment)
- **Foreign Keys**: `customer_id` → CUSTOMER (CASCADE)
- **Status Values**: pending, processing, shipped, completed, cancelled
- **Indexes**: `customer_id`, `order_date`

#### ORDER_ITEM
- **Purpose**: Junction table - connects orders with products
- **Primary Key**: `order_item_id` (auto-increment)
- **Foreign Keys**: 
  - `order_id` → ORDER (CASCADE)
  - `product_id` → PRODUCT (RESTRICT)
- **Why**: Many-to-Many relationship (one order has many products, one product in many orders)
- **Indexes**: Both foreign keys indexed

#### CART
- **Purpose**: Store active shopping carts
- **Primary Key**: `cart_id` (auto-increment)
- **Foreign Keys**: `customer_id` → CUSTOMER (CASCADE, UNIQUE)
- **Why**: One cart per customer for current session

#### CART_ITEM
- **Purpose**: Junction table - connects carts with products
- **Primary Key**: `cart_item_id` (auto-increment)
- **Foreign Keys**: 
  - `cart_id` → CART (CASCADE)
  - `product_id` → PRODUCT (CASCADE)
- **Unique Constraint**: `(cart_id, product_id)` - no duplicate products in cart
- **Indexes**: Both foreign keys indexed

### Key Design Decisions

1. **CASCADE vs RESTRICT**:
   - CASCADE on customer deletion: Remove orders when customer deleted
   - RESTRICT on product deletion: Prevent deletion if product in orders (data integrity)

2. **Indexes**: All foreign keys indexed for query performance

3. **Unique Constraints**: Prevent duplicate emails, category names, cart items

4. **Default Values**: Order status defaults to 'pending', stock to 0

---

## Setup & Installation

### Prerequisites
- Docker Desktop installed and running
- Git (for cloning repository)
- 4GB RAM minimum
- 10GB disk space

#### Optional: UV Package Manager
For local development without Docker:

**Windows (PowerShell)**:
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS/Linux**:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Verify installation**:
```powershell
uv --version
```

### Quick Start (One Command)

```powershell
cd backend
docker compose up -d
```

That's it! The system automatically:
1. ✅ Starts PostgreSQL database
2. ✅ Runs database migrations
3. ✅ Creates admin user (admin/admin123)
4. ✅ Loads sample data
5. ✅ Starts Django server

### Access Points
- **Application**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin/
- **API Base**: http://localhost:8000/shop/api/
- **Database**: localhost:5432

### Environment Configuration

The `.env` file contains:
```env
DATABASE_ENGINE=postgresql
DATABASE_NAME=webshop_db
DATABASE_USERNAME=webshop_user
DATABASE_PASSWORD=webshop_password
DATABASE_HOST=db
DATABASE_PORT=5432
DJANGO_SECRET_KEY=your-secret-key
DEBUG=1
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

### Manual Setup (Alternative)

If you need to set up manually:

```powershell
# 1. Navigate to backend
cd backend

# 2. Start database only
docker compose up -d db

# 3. Build web container
docker compose build web

# 4. Run migrations
docker compose exec web python manage.py migrate

# 5. Create superuser
docker compose exec web python manage.py createsuperuser

# 6. Load sample data
docker compose exec web python manage.py load_sample_data

# 7. Start server
docker compose up -d web
```

### Verification

Test the API:
```powershell
curl http://localhost:8000/shop/api/products/
```

Should return JSON array of products.

---

### Alternative: Local Setup with UV (Without Docker)

For development without Docker containers:

#### 1. Install UV (if not already installed)
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### 2. Create Virtual Environment
```powershell
cd backend
uv venv
```

#### 3. Activate Virtual Environment
**Windows**:
```powershell
.venv\Scripts\Activate.ps1
```

**macOS/Linux**:
```bash
source .venv/bin/activate
```

#### 4. Install Dependencies

**From pyproject.toml** (recommended):
```powershell
uv pip install -e .
```

**From requirements.txt** (alternative):
```powershell
uv pip install -r requirements.txt
```

#### 5. Set Up PostgreSQL
You'll need PostgreSQL running locally. Update `.env`:
```env
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

#### 6. Run Migrations
```powershell
python manage.py migrate
```

#### 7. Create Superuser
```powershell
python manage.py createsuperuser
```

#### 8. Load Sample Data
```powershell
python manage.py load_sample_data
```

#### 9. Start Development Server
```powershell
python manage.py runserver
```

### UV vs Pip Comparison

| Feature | UV | pip |
|---------|----|----- |
| Speed | 10-100x faster | Baseline |
| Dependency Resolution | Advanced, reliable | Basic |
| Lock Files | Built-in support | Requires pip-tools |
| Virtual Environments | Integrated (`uv venv`) | Separate tool (venv) |
| Written In | Rust | Python |
| Memory Usage | Lower | Higher |
| Installation | Single binary | Python package |

### Why UV?

1. **Speed**: UV is significantly faster for package installation
2. **Reliability**: Better dependency resolution prevents conflicts
3. **Modern**: Supports latest Python packaging standards (PEP 621, PEP 660)
4. **Developer Experience**: Single tool for venv + pip operations
5. **Production Ready**: Used by major projects and companies

---

## Project Structure

```
Challenge-III-Webshop/
│
├── backend/                          # Django backend application
│   │
│   ├── webshop/                      # Django project configuration
│   │   ├── __init__.py
│   │   ├── settings.py               # Django settings (DB, apps, middleware)
│   │   ├── urls.py                   # Main URL routing
│   │   ├── wsgi.py                   # WSGI entry point
│   │   └── asgi.py                   # ASGI entry point
│   │
│   ├── shop/                         # Main webshop app
│   │   ├── migrations/               # Database migration files
│   │   │   └── 0001_initial.py
│   │   ├── management/               # Custom Django commands
│   │   │   └── commands/
│   │   │       └── load_sample_data.py  # Load test data
│   │   ├── __init__.py
│   │   ├── models.py                 # ORM models (7 tables)
│   │   ├── views.py                  # API endpoints (8 endpoints)
│   │   ├── admin.py                  # Admin interface config
│   │   ├── urls.py                   # App-specific URL routing
│   │   └── apps.py                   # App configuration
│   │
│   ├── manage.py                     # Django CLI tool
│   ├── Dockerfile                    # Container definition
│   ├── compose.yml                   # Docker Compose config
│   ├── entrypoint.sh                 # Automation script
│   ├── pyproject.toml                # Modern Python project config (PEP 621)
│   ├── uv.lock                       # UV lock file for reproducible builds
│   ├── requirements.txt              # Python dependencies (legacy)
│   ├── .env                          # Environment variables
│   ├── .venv/                        # Virtual environment (local dev)
│   │
│   └── docs/
│       ├── SETUP_COMPLETE.md         # Quick start guide
│       ├── QUERIES.md                # ORM query examples
│       └── PROJECT_STRUCTURE.md      # Structure explanation
│
├── 01_create_tables.sql              # SQL reference files
├── 02_insert_sample_data.sql
├── 03_queries.sql
└── README.md
```

### Why This Structure?

#### `webshop/` (Project Directory)
- **Purpose**: Global Django configuration
- **Contains**: Settings, main URL routing, WSGI/ASGI
- **Reason**: Separates configuration from business logic

#### `shop/` (App Directory)
- **Purpose**: Webshop business logic
- **Contains**: Models, views, admin, custom commands
- **Reason**: Modular, reusable, maintainable

#### `pyproject.toml` (Modern Python Configuration)
- **Purpose**: Centralized project metadata and dependencies
- **Contains**: Package name, version, dependencies, build system
- **Reason**: Modern standard (PEP 621), replaces setup.py and setup.cfg
- **Benefits**: Single source of truth, better tooling support

#### `uv.lock` (Dependency Lock File)
- **Purpose**: Lock exact versions for reproducible installations
- **Contains**: Complete dependency tree with hashes
- **Reason**: Ensures consistent environments across machines
- **Usage**: Committed to version control

#### Benefits of Django Project/App Structure
1. **Modularity**: Easy to add new features as apps
2. **Reusability**: Apps can be moved to other projects
3. **Maintainability**: Clear separation of concerns
4. **Scalability**: Multiple apps can coexist (e.g., blog, accounts, shop)

---

## API Documentation

### Base URL
```
http://localhost:8000/shop/api/
```

### Endpoints

#### 1. Get All Products
```http
GET /shop/api/products/
```
**Response**: Array of products with category information
```json
[
  {
    "product_id": 1,
    "name": "Elegant Marble Gloves",
    "price": "235.99",
    "stock": 58,
    "category": "Home"
  }
]
```

#### 2. Get Customer Orders
```http
GET /shop/api/customer/<customer_id>/orders/
```
**Response**: Array of customer's orders
```json
[
  {
    "order_id": 1,
    "order_date": "2025-11-26",
    "status": "completed",
    "total_amount": "910.65",
    "customer_email": "deborah.bruen@example.com"
  }
]
```

#### 3. Get Order Details
```http
GET /shop/api/order/<order_id>/
```
**Response**: Order with all line items
```json
[
  {
    "order_id": 1,
    "order_date": "2025-11-26",
    "customer_name": "Deborah Bruen",
    "product_name": "Elegant Marble Gloves",
    "quantity": 2,
    "price_per_unit": "235.99",
    "subtotal": "471.98"
  }
]
```

#### 4. Get Customer Cart
```http
GET /shop/api/customer/<customer_id>/cart/
```
**Response**: Cart contents with total
```json
{
  "customer_id": 1,
  "items": [
    {
      "product_name": "Handmade Wooden Computer",
      "price": "369.35",
      "quantity": 2,
      "subtotal": "738.70"
    }
  ],
  "total": "738.70"
}
```

#### 5. Get Bestsellers
```http
GET /shop/api/bestsellers/
```
**Response**: Top 10 products by sales
```json
[
  {
    "product_id": 1,
    "name": "Elegant Marble Gloves",
    "price": "235.99",
    "total_sold": 150,
    "total_revenue": "35398.50"
  }
]
```

#### 6. Get Low Stock Products
```http
GET /shop/api/low-stock/
```
**Response**: Products with stock < 10
```json
[
  {
    "product_id": 3,
    "name": "Handmade Wooden Computer",
    "price": "369.35",
    "stock": 2,
    "category": "Electronics"
  }
]
```

#### 7. Get Customer Statistics
```http
GET /shop/api/customer-stats/
```
**Response**: Customer spending analysis
```json
[
  {
    "customer_id": 1,
    "name": "Deborah Bruen",
    "email": "deborah.bruen@example.com",
    "total_orders": 5,
    "total_spent": "4553.25"
  }
]
```

#### 8. Get Category Statistics
```http
GET /shop/api/category-stats/
```
**Response**: Product distribution by category
```json
[
  {
    "category_name": "Electronics",
    "product_count": 15,
    "total_stock": 450,
    "avg_price": "525.75"
  }
]
```

### Error Responses

**404 Not Found**:
```json
{
  "error": "Cart not found"
}
```

---

## Django ORM Usage

### Basic Queries

```python
from shop.models import Product, Customer, Order

# Get all products
products = Product.objects.all()

# Filter products
electronics = Product.objects.filter(category__category_name='Electronics')
expensive = Product.objects.filter(price__gte=500)

# Get with related data (JOIN)
products = Product.objects.select_related('category').all()

# Get single object
product = Product.objects.get(product_id=1)
```

### Relationships

```python
# Get customer's orders (1:n)
customer = Customer.objects.get(customer_id=1)
orders = customer.orders.all()

# Get order items (reverse FK)
order = Order.objects.get(order_id=1)
items = order.items.select_related('product').all()

# Get products in category (reverse FK)
category = Category.objects.get(category_name='Electronics')
products = category.products.all()
```

### Aggregations

```python
from django.db.models import Sum, Count, Avg, F

# Total revenue per product
Product.objects.annotate(
    revenue=Sum(F('order_items__quantity') * F('order_items__price_per_unit'))
)

# Customer order statistics
Customer.objects.annotate(
    order_count=Count('orders'),
    total_spent=Sum('orders__total_amount')
).order_by('-total_spent')

# Category summary
Category.objects.annotate(
    product_count=Count('products'),
    avg_price=Avg('products__price')
)
```

### Complex Queries

```python
from django.db.models import Q
from datetime import datetime, timedelta

# OR condition
Product.objects.filter(Q(stock__lt=10) | Q(price__gt=1000))

# Recent orders
recent = Order.objects.filter(
    order_date__gte=datetime.now().date() - timedelta(days=30)
)

# Products never ordered
Product.objects.filter(order_items__isnull=True)

# Customers who spent > $500
Customer.objects.annotate(
    total=Sum('orders__total_amount')
).filter(total__gt=500)
```

### Creating & Updating

```python
# Create customer
customer = Customer.objects.create(
    first_name='John',
    last_name='Doe',
    email='john@example.com',
    password='hashed_password'
)

# Update product
product = Product.objects.get(product_id=1)
product.stock = 100
product.save()

# Bulk update
Product.objects.filter(category__category_name='Electronics').update(
    stock=F('stock') + 10
)
```

### Transactions

```python
from django.db import transaction

with transaction.atomic():
    # Create order
    order = Order.objects.create(customer=customer, total_amount=0)
    
    # Add items
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price_per_unit=item.product.price
        )
        
        # Update stock
        item.product.stock -= item.quantity
        item.product.save()
    
    # Clear cart
    cart.items.all().delete()
```

---

## Development Workflow

### Starting Development

#### With Docker:
```powershell
# Start services
cd backend
docker compose up -d

# View logs
docker compose logs -f web

# Access Django shell
docker compose exec web python manage.py shell
```

#### With UV (Local):
```powershell
# Navigate to project
cd backend

# Activate virtual environment
.venv\Scripts\Activate.ps1

# Install/update dependencies
uv pip sync  # From uv.lock (exact versions)
# OR
uv pip install -e .  # From pyproject.toml

# Start development server
python manage.py runserver

# Access Django shell
python manage.py shell
```

### Making Changes

#### 1. Model Changes

```powershell
# After modifying models.py
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
```

#### 2. Adding New Views

Edit `shop/views.py` and `shop/urls.py` - changes apply immediately (hot-reload enabled).

#### 3. Running Management Commands

```powershell
docker compose exec web python manage.py <command>
```

### Testing

```powershell
# Run tests
docker compose exec web python manage.py test

# Test specific app
docker compose exec web python manage.py test shop

# Django shell for manual testing
docker compose exec web python manage.py shell
```

### Database Operations

```powershell
# Connect to PostgreSQL
docker compose exec db psql -U webshop_user -d webshop_db

# Database backup
docker compose exec db pg_dump -U webshop_user webshop_db > backup.sql

# Restore database
docker compose exec -T db psql -U webshop_user webshop_db < backup.sql

# Reset database (WARNING: deletes all data)
docker compose down -v
docker compose up -d
```

### Stopping Services

```powershell
# Stop containers (keep data)
docker compose stop

# Stop and remove containers (keep data)
docker compose down

# Stop and remove everything including data
docker compose down -v
```

---

## Deployment

### Production Considerations

#### 1. Environment Variables

Update `.env` for production:
```env
DEBUG=0
DJANGO_SECRET_KEY=<generate-strong-random-key>
DJANGO_ALLOWED_HOSTS=yourdomain.com
DATABASE_PASSWORD=<strong-password>
```

#### 2. Use Production Server

The Dockerfile already includes gunicorn. Update `entrypoint.sh` CMD:
```bash
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "webshop.wsgi:application"]
```

#### 3. Static Files

```powershell
docker compose exec web python manage.py collectstatic --noinput
```

#### 4. Database Migrations

Always run before deployment:
```powershell
docker compose exec web python manage.py migrate --noinput
```

#### 5. Security Checklist

- [ ] DEBUG=0
- [ ] Strong SECRET_KEY
- [ ] Strong database password
- [ ] HTTPS enabled
- [ ] CORS configured
- [ ] Rate limiting implemented
- [ ] SQL injection protection (Django ORM provides this)
- [ ] XSS protection enabled
- [ ] CSRF protection enabled

### Docker Production Build

```dockerfile
# Use production command
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "webshop.wsgi:application"]
```

### Scaling

Horizontal scaling with multiple web containers:
```yaml
services:
  web:
    deploy:
      replicas: 3
```

Add load balancer (nginx) in front of Django containers.

---

## Troubleshooting

### Common Issues

#### Port Already in Use
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process
taskkill /PID <process_id> /F
```

#### Database Connection Errors
```powershell
# Check if database is running
docker compose ps

# Check database logs
docker compose logs db

# Restart database
docker compose restart db
```

#### Migration Errors
```powershell
# Show migration status
docker compose exec web python manage.py showmigrations

# Fake migration (if needed)
docker compose exec web python manage.py migrate --fake

# Reset migrations (DANGER: loses data)
docker compose exec web python manage.py migrate shop zero
```

#### Permission Errors
```powershell
# Fix entrypoint permissions
docker compose exec web chmod +x /app/entrypoint.sh
```

### Logging

View application logs:
```powershell
# All logs
docker compose logs

# Specific service
docker compose logs web
docker compose logs db

# Follow logs
docker compose logs -f

# Last 100 lines
docker compose logs --tail=100
```

---

## Maintenance

### Regular Tasks

#### Backup Database
```powershell
docker compose exec db pg_dump -U webshop_user webshop_db > backup_$(date +%Y%m%d).sql
```

#### Update Dependencies

**Docker approach**:
```powershell
# Update requirements.txt
# Rebuild container
docker compose build --no-cache web
docker compose up -d
```

**UV approach**:
```powershell
# Add new dependency to pyproject.toml
uv add django-cors-headers

# Or add to pyproject.toml manually, then:
uv pip compile pyproject.toml -o requirements.txt
uv pip sync

# Update all dependencies
uv pip install --upgrade -e .

# Generate lock file
uv pip freeze > uv.lock
```

#### Clean Old Data
```python
# In Django shell
from datetime import datetime, timedelta
from shop.models import Order

# Delete orders older than 1 year
old_date = datetime.now().date() - timedelta(days=365)
Order.objects.filter(order_date__lt=old_date, status='completed').delete()
```

### Performance Monitoring

Add monitoring tools:
- Django Debug Toolbar (development)
- Django Silk (profiling)
- Sentry (error tracking)
- Prometheus + Grafana (metrics)

---

## Conclusion

This webshop backend provides a solid foundation for an e-commerce platform with:

✅ **Complete database schema** following relational design principles
✅ **Django ORM** for type-safe, maintainable database operations
✅ **RESTful API** for frontend integration
✅ **Docker containerization** for consistent deployments
✅ **Automated setup** reducing onboarding time
✅ **Admin interface** for easy data management
✅ **Scalable architecture** ready for production

### Next Steps

1. Add authentication & authorization (Django REST Framework + JWT)
2. Implement shopping cart operations (add/remove/update)
3. Add order processing workflow
4. Integrate payment gateway
5. Add product search & filtering
6. Implement email notifications
7. Add rate limiting & caching
8. Create frontend application

---

## Support & Resources

- **Django Documentation**: https://docs.djangoproject.com/
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/
- **Docker Documentation**: https://docs.docker.com/
- **Project Repository**: https://github.com/hieni/Challenge-III-Webshop

---

**Version**: 1.0.0  
**Last Updated**: November 26, 2025  
**Author**: Development Team
