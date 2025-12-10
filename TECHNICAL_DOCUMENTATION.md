# Technical Documentation - Webshop Application

**Version:** 1.0  
**Date:** December 10, 2025  
**Framework:** Django 5.2.8  
**Database:** PostgreSQL 17  
**Python:** 3.13+

---

## Executive Summary

This document provides an unbiased technical analysis of the webshop Django application. The system implements a complete e-commerce platform with customer authentication, shopping cart, checkout, order management, and wishlist functionality. The application uses session-based authentication and runs in a Docker containerized environment.

---

## 1. Architecture Overview

### 1.1 Application Structure

```
webshop/
├── webshop/                 # Django project configuration
│   ├── settings.py         # Configuration and database setup
│   ├── urls.py             # Root URL routing
│   ├── wsgi.py / asgi.py   # WSGI/ASGI entry points
│   └── .venv/              # Virtual environment
├── shop/                    # Main application
│   ├── models.py           # Data models (429 lines)
│   ├── views.py            # Product views and cart operations
│   ├── views_cart.py       # Cart and checkout logic (168 lines)
│   ├── views_login.py      # Authentication views
│   ├── views_order.py      # Order display views
│   ├── views_product.py    # Product detail view
│   ├── views_wishlist.py   # Wishlist operations
│   ├── urls.py             # URL routing
│   ├── admin.py            # Admin panel registration
│   ├── templates/          # HTML templates (11 files)
│   ├── static/             # Static assets
│   └── fixtures/           # Initial data (data.yaml)
├── manage.py               # Django CLI
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container image definition
├── compose.yml             # Docker Compose orchestration
└── init.sh                 # Container initialization script
```

### 1.2 Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | Django | 5.2.8 |
| Database | PostgreSQL | 17 |
| Container | Docker | Latest |
| Python | CPython | 3.13-slim |
| Frontend | Bootstrap | 4.x |
| Icons | Font Awesome | 5.x |
| WSGI Server | Gunicorn | 23.0.0 |

---

## 2. Data Model Architecture

### 2.1 Entity Relationship Overview

The application implements 11 models across three primary domains:

1. **Customer Domain**: Customer, Address
2. **Product Domain**: Product, Category
3. **Transaction Domain**: Order, OrderItem, Payment, Shipment, Cart, CartItem, Wishlist, WishlistItem

### 2.2 Model Specifications

#### 2.2.1 Customer Model

**Purpose:** User account management with authentication and address relationships.

**Fields:**
- `first_name` (CharField, max_length=50): Customer first name
- `last_name` (CharField, max_length=50): Customer last name
- `email` (EmailField, unique=True): Authentication identifier
- `password_hash` (CharField, max_length=128): Hashed password
- `default_billing_address` (ForeignKey to Address, nullable): Default billing address reference
- `default_shipping_address` (ForeignKey to Address, nullable): Default shipping address reference

**Methods:**
- `set_password(raw_password)`: Hashes password using Django's make_password
- `check_password(raw_password)`: Validates password against hash
- `__str__()`: Returns formatted name with email

**Relationships:**
- OneToOne with Cart (cart)
- OneToOne with Wishlist (wishlist)
- OneToMany with Order (orders)
- OneToMany with Address (addresses)

**Meta:**
- Ordering: `['last_name', 'first_name']`
- Verbose name: "Kunde" / "Kunden"

**Technical Notes:**
- Uses Django's built-in password hashing (PBKDF2 by default)
- Email uniqueness enforced at database level
- Default addresses use SET_NULL on deletion to prevent data loss

#### 2.2.2 Address Model

**Purpose:** Store customer addresses for billing and shipping.

**Fields:**
- `customer` (ForeignKey to Customer): Owner of address
- `street` (CharField, max_length=100): Street address
- `city` (CharField, max_length=50): City name
- `postal_code` (CharField, max_length=20): Postal/ZIP code
- `country` (CharField, max_length=50, default="Germany"): Country name

**Relationships:**
- ManyToOne with Customer (customer)
- OneToMany with Order (billing_orders, shipment_orders as billing_address/shipment_address)

**Meta:**
- Verbose name: "Adresse" / "Adressen"

**Technical Notes:**
- Cascade deletion when customer is deleted
- Can be referenced by multiple orders (PROTECT on_delete)
- No uniqueness constraints - customers can have multiple addresses

#### 2.2.3 Category Model

**Purpose:** Product categorization.

**Fields:**
- `category_name` (CharField, max_length=50, unique=True): Category identifier

**Relationships:**
- OneToMany with Product (products)

**Meta:**
- Ordering: `['category_name']`
- Verbose name: "Kategorie" / "Kategorien"

**Technical Notes:**
- Simple taxonomy structure (no nested categories)
- Name uniqueness enforced at database level

#### 2.2.4 Product Model

**Purpose:** Product catalog with inventory management.

**Fields:**
- `name` (CharField, max_length=100): Product name
- `description` (TextField): Product description
- `price` (DecimalField, max_digits=10, decimal_places=2): Unit price
- `stock` (IntegerField, default=0): Available quantity
- `category` (ForeignKey to Category): Product category
- `image` (ImageField, upload_to="products/", nullable): Product image

**Validators:**
- `price`: MinValueValidator(Decimal('0.01'))
- `stock`: MinValueValidator(0)

**Methods:**
- `is_in_stock()`: Returns True if stock > 0
- `is_low_stock()`: Returns True if 0 < stock ≤ 5
- `__str__()`: Returns name with price

**Relationships:**
- ManyToOne with Category (category)
- OneToMany with OrderItem (implicit)
- OneToMany with CartItem (implicit)
- OneToMany with WishlistItem (implicit)

**Meta:**
- Ordering: `['name']`
- Verbose name: "Produkt" / "Produkte"

**Technical Notes:**
- Stock managed at product level (no warehouse/location tracking)
- Decimal type used for precise currency calculations
- Image storage handled by Django's FileField

#### 2.2.5 Order Model

**Purpose:** Customer purchase orders with status tracking.

**Fields:**
- `customer` (ForeignKey to Customer): Order owner
- `billing_address` (ForeignKey to Address, PROTECT): Billing address (required)
- `shipment_address` (ForeignKey to Address, PROTECT): Shipping address (required)
- `order_date` (DateTimeField, auto_now_add=True): Creation timestamp
- `status` (CharField, max_length=20, choices): Current order status
- `total_amount` (DecimalField, max_digits=10, decimal_places=2): Order total

**Status Choices:**
- `pending`: Ausstehend (initial state)
- `processing`: In Bearbeitung
- `shipped`: Versendet
- `delivered`: Zugestellt
- `cancelled`: Storniert

**Validators:**
- `total_amount`: MinValueValidator(Decimal('0.00'))

**Relationships:**
- ManyToOne with Customer (customer)
- ManyToOne with Address (billing_address) - PROTECT
- ManyToOne with Address (shipment_address) - PROTECT
- OneToMany with OrderItem (items)
- OneToOne with Payment (payment)
- OneToMany with Shipment (shipments)

**Meta:**
- Ordering: `['-order_date']` (newest first)
- Verbose name: "Bestellung" / "Bestellungen"

**Technical Notes:**
- PROTECT on_delete for addresses prevents deletion of addresses with active orders
- Both billing and shipping addresses are required (application-level enforcement)
- Total amount stored as snapshot (not recalculated from items)
- Status transitions not enforced at model level

#### 2.2.6 OrderItem Model

**Purpose:** Line items within an order.

**Fields:**
- `order` (ForeignKey to Order): Parent order
- `product` (ForeignKey to Product): Ordered product
- `quantity` (IntegerField): Quantity ordered
- `price_per_unit` (DecimalField, max_digits=10, decimal_places=2): Unit price at time of order

**Validators:**
- `quantity`: MinValueValidator(1)
- `price_per_unit`: MinValueValidator(Decimal('0.01'))

**Methods:**
- `get_subtotal()`: Returns quantity × price_per_unit

**Relationships:**
- ManyToOne with Order (order)
- ManyToOne with Product (product)

**Meta:**
- Verbose name: "Bestellposition" / "Bestellpositionen"

**Technical Notes:**
- Price stored at order time (protects against price changes)
- No composite unique constraint (same product can appear multiple times in order)
- Cascade deletion when order is deleted

#### 2.2.7 Cart Model

**Purpose:** Temporary shopping cart for customers.

**Fields:**
- `customer` (OneToOneField to Customer): Cart owner
- `last_updated` (DateTimeField, auto_now=True): Last modification timestamp

**Methods:**
- `get_total()`: Calculates sum of all CartItem subtotals

**Relationships:**
- OneToOne with Customer (customer)
- OneToMany with CartItem (items)

**Meta:**
- Verbose name: "Warenkorb" / "Warenkörbe"

**Technical Notes:**
- One cart per customer (enforced by OneToOneField)
- Auto-created when customer adds first item
- Not deleted when customer logs out (persistent cart)

#### 2.2.8 CartItem Model

**Purpose:** Individual items in shopping cart.

**Fields:**
- `cart` (ForeignKey to Cart): Parent cart
- `product` (ForeignKey to Product): Product reference
- `quantity` (IntegerField): Quantity in cart

**Validators:**
- `quantity`: MinValueValidator(1)

**Methods:**
- `get_subtotal()`: Returns quantity × product.price

**Relationships:**
- ManyToOne with Cart (cart)
- ManyToOne with Product (product)

**Meta:**
- Unique together: `['cart', 'product']` (prevents duplicate products in same cart)
- Verbose name: "Warenkorb-Position" / "Warenkorb-Positionen"

**Technical Notes:**
- Composite unique constraint enforced at database level
- Price calculated dynamically from Product model (not stored)
- Cascade deletion when cart is deleted

#### 2.2.9 Wishlist Model

**Purpose:** Customer product wishlist.

**Fields:**
- `customer` (OneToOneField to Customer): Wishlist owner
- `last_updated` (DateTimeField, auto_now=True): Last modification timestamp

**Relationships:**
- OneToOne with Customer (customer)
- OneToMany with WishlistItem (items)

**Meta:**
- Verbose name: "Wunschliste" / "Wunschlisten"

**Technical Notes:**
- One wishlist per customer
- Similar structure to Cart model

#### 2.2.10 WishlistItem Model

**Purpose:** Products saved in wishlist.

**Fields:**
- `wishlist` (ForeignKey to Wishlist): Parent wishlist
- `product` (ForeignKey to Product): Product reference

**Relationships:**
- ManyToOne with Wishlist (wishlist)
- ManyToOne with Product (product)

**Meta:**
- Unique together: `['wishlist', 'product']`
- Verbose name: "Wunschlisten-Position" / "Wunschlisten-Positionen"

**Technical Notes:**
- No quantity field (wishlist is binary: product is in or not)
- Composite unique constraint prevents duplicates

#### 2.2.11 Payment Model

**Purpose:** Payment transaction tracking.

**Fields:**
- `order` (OneToOneField to Order): Associated order
- `amount` (DecimalField, max_digits=10, decimal_places=2): Payment amount
- `payment_date` (DateTimeField, auto_now_add=True): Transaction timestamp
- `payment_method` (CharField, max_length=32, choices): Payment method
- `status` (CharField, max_length=20, choices): Payment status
- `transaction_id` (CharField, max_length=200, blank=True): External transaction reference

**Payment Method Choices:**
- `paypal`: PayPal
- `credit_card`: Kreditkarte
- `invoice`: Rechnung
- `bank_transfer`: Überweisung

**Payment Status Choices:**
- `pending`: Ausstehend (initial state)
- `completed`: Abgeschlossen
- `failed`: Fehlgeschlagen
- `refunded`: Erstattet

**Validators:**
- `amount`: MinValueValidator(Decimal('0.00'))

**Relationships:**
- OneToOne with Order (order)

**Meta:**
- Ordering: `['-payment_date']`
- Verbose name: "Zahlung" / "Zahlungen"

**Technical Notes:**
- One payment per order (OneToOneField)
- Amount stored independently (should match order.total_amount)
- No actual payment gateway integration (placeholder implementation)
- Transaction ID field ready for integration

#### 2.2.12 Shipment Model

**Purpose:** Shipment tracking for orders.

**Fields:**
- `order` (ForeignKey to Order): Associated order
- `shipped_date` (DateTimeField, nullable): Date shipped
- `delivery_date` (DateTimeField, nullable): Date delivered
- `carrier` (CharField, max_length=100, blank=True): Shipping carrier name
- `tracking_number` (CharField, max_length=200, blank=True): Tracking number
- `status` (CharField, max_length=20, choices): Shipment status

**Shipment Status Choices:**
- `pending`: Ausstehend (initial state)
- `preparing`: Wird vorbereitet
- `shipped`: Versendet
- `in_transit`: Unterwegs
- `delivered`: Zugestellt
- `returned`: Zurückgesendet

**Methods:**
- `get_tracking_url()`: Generates carrier-specific tracking URL

**Relationships:**
- ManyToOne with Order (order)

**Meta:**
- Ordering: `['-shipped_date']`
- Verbose name: "Versand" / "Versendungen"

**Technical Notes:**
- Multiple shipments per order supported (ForeignKey, not OneToOne)
- Tracking URL generation for DHL, DPD, UPS, Hermes
- Dates nullable (set when status changes)

### 2.3 Data Model Issues and Observations

#### Critical Observations:

1. **Address Deletion Protection**: Order model uses PROTECT on_delete for addresses, preventing accidental deletion of addresses with active orders. This is correct but may cause issues if customer wants to delete old addresses.

2. **Price Consistency**: OrderItem stores `price_per_unit` at order time (correct), but CartItem calculates from Product dynamically. This means cart totals can change if prices are updated.

3. **Stock Management**: Stock is decremented at checkout but no stock reservation system exists. Concurrent checkouts could potentially oversell products.

4. **Payment Integration**: Payment model exists but no actual payment gateway integration. Status must be manually updated.

5. **Shipment Model Cardinality**: Shipment uses ForeignKey (one-to-many) but current implementation creates single shipment per order. Unclear if multiple shipments per order are intended.

#### Non-Critical Observations:

1. **No Soft Deletes**: All models use hard deletion. No audit trail for deleted records.

2. **No Created/Updated Timestamps**: Most models lack created_at/updated_at fields (except Order, Cart, Wishlist).

3. **No User Model Integration**: Uses custom Customer model instead of Django's built-in User model. Session-based authentication instead of Django auth framework.

4. **Minimal Validation**: Most business logic validation happens in views, not at model level.

5. **No Order Total Validation**: Order.total_amount is stored but not validated against sum of OrderItem subtotals.

---

## 3. View Layer Architecture

### 3.1 View Distribution

The application separates views into 6 modules:

| Module | Lines | Views | Purpose |
|--------|-------|-------|---------|
| views.py | ~94 | 3 | Home, product listing, add to cart |
| views_cart.py | 168 | 5 | Cart operations and checkout |
| views_login.py | ~94 | 3 | Authentication (register, login, logout) |
| views_order.py | ~14 | 2 | Order listing and detail |
| views_product.py | ~7 | 1 | Product detail page |
| views_wishlist.py | ~33 | 2 | Wishlist operations |

**Total:** 16 view functions across 6 modules

### 3.2 View Function Analysis

#### 3.2.1 views.py

##### home(request)
- **Purpose**: Landing page
- **Template**: home.html
- **Authentication**: Not required
- **Logic**: Simple render

##### product_list(request)
- **Purpose**: Display products with filtering and sorting
- **Template**: products.html
- **Authentication**: Not required
- **Query Parameters**:
  - `category`: Filter by category ID
  - `min_price`, `max_price`: Price range filter
  - `search`: Text search in name/description
  - `sort`: Sorting (name, price_asc, price_desc)
- **Database Queries**: 
  - All products
  - All categories
  - Filtered/sorted product subset
- **Optimization Opportunity**: No select_related or prefetch_related used

##### add_to_cart(request, product_id)
- **Purpose**: Add product to cart or increase quantity
- **Authentication**: Required (session customer_id)
- **Logic**:
  1. Check authentication
  2. Verify product stock
  3. Get or create cart
  4. Get or create cart item
  5. Increase quantity if exists
  6. Update session cart count
- **Database Operations**: 
  - 1 Customer SELECT
  - 1 Product SELECT (with get_object_or_404)
  - 1-2 Cart SELECT/INSERT
  - 1-2 CartItem SELECT/INSERT or UPDATE
  - 1 CartItem aggregate query for count
- **Stock Validation**: Checks product.stock before adding
- **Race Condition Risk**: No transaction or locking mechanism

#### 3.2.2 views_cart.py

##### cart_view(request)
- **Purpose**: Display shopping cart
- **Template**: cart.html
- **Authentication**: Required
- **Logic**:
  1. Get customer cart
  2. Calculate item totals (in Python)
  3. Calculate grand total
- **Database Queries**: 
  - 1 Customer SELECT
  - 1-2 Cart SELECT/INSERT
  - 1 CartItem SELECT with filter
- **Optimization**: Totals calculated in Python, could use database aggregation

##### cart_increase(request, item_id)
- **Purpose**: Increase cart item quantity by 1
- **Authentication**: Implicit (via item_id)
- **Validation**: Checks if quantity < stock
- **Session Update**: Updates cart_items_count
- **Database Operations**: 
  - 1 CartItem SELECT
  - 1 CartItem UPDATE
  - 1 CartItem aggregate query for count

##### cart_decrease(request, item_id)
- **Purpose**: Decrease quantity by 1 or remove if quantity = 1
- **Authentication**: Implicit
- **Logic**: Deletes item if quantity would reach 0
- **Session Update**: Updates cart_items_count
- **Database Operations**: 
  - 1 CartItem SELECT
  - 1 CartItem UPDATE or DELETE
  - 1 CartItem aggregate query for count

##### cart_remove(request, item_id)
- **Purpose**: Remove item from cart
- **Authentication**: Implicit
- **Session Update**: Updates cart_items_count
- **Database Operations**: 
  - 1 CartItem SELECT
  - 1 CartItem DELETE
  - 1 CartItem aggregate query for count

##### checkout(request)
- **Purpose**: Display checkout form (GET) or process order (POST)
- **Template**: checkout.html
- **Authentication**: Required
- **GET Logic**:
  1. Fetch cart items
  2. Check cart not empty
  3. Calculate total
  4. Render form
- **POST Logic**:
  1. Validate stock availability
  2. Create billing address
  3. Create shipping address (or reuse billing)
  4. Create order with total_amount
  5. Create order items
  6. Decrement product stock
  7. Create payment record (status=pending)
  8. Create shipment record (status=pending)
  9. Delete cart items
  10. Reset session cart count to 0
  11. Redirect to order detail
- **Database Operations (POST)**: 
  - 1 Customer SELECT
  - 1 Cart SELECT
  - N CartItem SELECT
  - N Product stock checks
  - 1-2 Address INSERT (depending on same_as_billing)
  - 1 Order INSERT
  - N OrderItem INSERT
  - N Product UPDATE (stock decrement)
  - 1 Payment INSERT
  - 1 Shipment INSERT
  - N CartItem DELETE
- **Transaction Safety**: No explicit transaction wrapping (uses Django's default behavior)
- **Stock Race Condition**: Multiple users checking out same product could cause overselling

**Critical Issue**: No atomic transaction around stock check and decrement. Consider:
```python
from django.db import transaction

with transaction.atomic():
    # Lock products for update
    for item in cart_items:
        product = Product.objects.select_for_update().get(id=item.product.id)
        if product.stock < item.quantity:
            raise ValueError("Insufficient stock")
        product.stock -= item.quantity
        product.save()
```

#### 3.2.3 views_login.py

##### register_view(request)
- **Purpose**: User registration with address
- **Template**: register.html
- **Method**: GET (form) and POST (submission)
- **POST Logic**:
  1. Validate password match
  2. Check email uniqueness
  3. Create customer with hashed password
  4. Create address
  5. Set default addresses
  6. Create session
  7. Redirect to product list
- **Database Operations**: 
  - 1 Customer SELECT (exists check)
  - 1 Customer INSERT
  - 1 Address INSERT
  - 1 Customer UPDATE (for default addresses)
- **Security**: Password hashed using Customer.set_password()
- **Session Management**: Sets customer_id in session

##### login_view(request)
- **Purpose**: Customer authentication
- **Template**: login.html
- **Method**: GET (form) and POST (submission)
- **POST Logic**:
  1. Fetch customer by email
  2. Verify password hash
  3. Create session
  4. Redirect to product list
- **Database Operations**: 
  - 1 Customer SELECT by email
- **Security**: Uses Customer.check_password() method
- **Session Management**: Sets customer_id and customer_name

##### logout_view(request)
- **Purpose**: End user session
- **Logic**: Flush entire session
- **Redirect**: Login page
- **Session Impact**: All session data cleared (cart count lost)

#### 3.2.4 views_order.py

##### orders_list(request)
- **Purpose**: Display customer's order history
- **Template**: orders.html
- **Authentication**: Required (implicit, no check)
- **Database Queries**: 
  - 1 Customer SELECT
  - 1 Order SELECT with filter and order_by
- **Ordering**: Newest first (-order_date)
- **Missing**: Pagination for large order histories

##### order_detail(request, order_id)
- **Purpose**: Display single order details
- **Template**: order_detail.html
- **Authentication**: Not checked (security issue)
- **Database Queries**: 
  - 1 Order SELECT
  - 1 OrderItem SELECT with filter
- **Security Issue**: No validation that order belongs to logged-in customer

**Critical Security Issue**: Any customer can view any order by changing order_id in URL. Should validate:
```python
customer_id = request.session.get("customer_id")
order = Order.objects.get(id=order_id, customer_id=customer_id)
```

#### 3.2.5 views_product.py

##### product_detail(request, product_id)
- **Purpose**: Display single product details
- **Template**: product_detail.html
- **Authentication**: Not required
- **Database Queries**: 
  - 1 Product SELECT
- **Error Handling**: No get_object_or_404 (raises DoesNotExist)

#### 3.2.6 views_wishlist.py

##### wishlist_view(request)
- **Purpose**: Display customer wishlist
- **Template**: wishlist.html
- **Authentication**: Required
- **Database Queries**: 
  - 1 Customer SELECT
  - 1-2 Wishlist SELECT/INSERT
  - 1 WishlistItem SELECT with filter

##### wishlist_add(request, product_id)
- **Purpose**: Add product to wishlist
- **Authentication**: Required
- **Logic**: Uses get_or_create (prevents duplicates)
- **Database Operations**: 
  - 1 Customer SELECT
  - 1-2 Wishlist SELECT/INSERT
  - 1-2 WishlistItem SELECT/INSERT
- **Redirect**: Back to product_detail

### 3.3 View Layer Issues and Observations

#### Critical Issues:

1. **Order Detail Security Vulnerability**: No authorization check in `order_detail()` allows any user to view any order.

2. **Checkout Race Condition**: Stock check and decrement not atomic. Multiple concurrent checkouts can oversell products.

3. **Missing Authentication Guards**: Several views assume customer_id exists without checking.

4. **No CSRF Token Verification**: Not visible in code review but should be verified in templates.

#### Performance Issues:

1. **N+1 Query Problem**: `product_list` doesn't use `select_related('category')` when filtering by category.

2. **Cart Total Calculation**: Calculated in Python instead of database aggregation.

3. **Missing Pagination**: Order history and product listing have no pagination.

4. **Repeated Count Queries**: Session cart count requires aggregate query on every cart modification.

#### Code Quality Issues:

1. **Inconsistent Error Handling**: Mix of `get()` (raises exception) and `get_object_or_404()`.

2. **Magic Strings**: Status values ("pending", "completed") hardcoded instead of using model constants.

3. **Business Logic in Views**: Stock validation, total calculation in views instead of model methods or service layer.

4. **No Form Classes**: Form validation done manually in views instead of using Django Forms.

5. **Session Dependency**: Heavy reliance on session state instead of database queries (cart count).

---

## 4. URL Routing Structure

### 4.1 URL Configuration

**File**: `shop/urls.py`

| URL Pattern | View Function | URL Name | HTTP Methods |
|-------------|---------------|----------|--------------|
| `` | views.home | home | GET |
| `products/` | views.product_list | product_list | GET |
| `login/` | views_login.login_view | login | GET, POST |
| `logout/` | views_login.logout_view | logout | GET |
| `add_to_cart/<int:product_id>/` | views.add_to_cart | add_to_cart | POST |
| `cart/` | views_cart.cart_view | cart | GET |
| `cart/increase/<int:item_id>/` | views_cart.cart_increase | cart_increase | POST |
| `cart/decrease/<int:item_id>/` | views_cart.cart_decrease | cart_decrease | POST |
| `cart/remove/<int:item_id>/` | cart_remove | cart_remove | POST |
| `checkout/` | views_cart.checkout | checkout | GET, POST |
| `orders/` | views_order.orders_list | orders_list | GET |
| `orders/<int:order_id>/` | views_order.order_detail | order_detail | GET |
| `product/<int:product_id>/` | views_product.product_detail | product_detail | GET |
| `wishlist/` | views_wishlist.wishlist_view | wishlist | GET |
| `wishlist/add/<int:product_id>/` | views_wishlist.wishlist_add | wishlist_add | POST |
| `register/` | views_login.register_view | register | GET, POST |

**Total URLs**: 16

### 4.2 URL Structure Analysis

**Observations:**

1. **RESTful Naming**: Partially follows REST conventions but inconsistent:
   - Good: `/orders/`, `/products/`
   - Non-RESTful: `/cart/increase/` (should be PATCH to `/cart/items/<id>/`)

2. **HTTP Method Usage**: All mutations use GET (via redirects from POST). No proper POST/PUT/DELETE distinction.

3. **No API Endpoints**: All views return HTML templates. No JSON API for frontend frameworks.

4. **Redundant URL Import**: `from django.shortcuts import render` imported but not used in urls.py (Ruff reported this).

5. **URL Naming Convention**: Consistent use of snake_case for URL names.

---

## 5. Template Structure

### 5.1 Template Files

| Template | Purpose | Extends | Lines (est.) |
|----------|---------|---------|--------------|
| base.html | Base layout with navbar | - | ~150 |
| home.html | Landing page | base.html | ~50 |
| products.html | Product listing | base.html | ~100 |
| product_detail.html | Single product | base.html | ~80 |
| cart.html | Shopping cart | base.html | ~120 |
| checkout.html | Checkout form | base.html | ~180 |
| orders.html | Order history | base.html | ~70 |
| order_detail.html | Order details | base.html | ~100 |
| login.html | Login form | base.html | ~60 |
| register.html | Registration form | base.html | ~100 |
| wishlist.html | Wishlist | base.html | ~80 |

**Total**: 11 templates

### 5.2 Template Analysis

**Observations:**

1. **Template Inheritance**: All templates extend base.html (consistent pattern).

2. **Bootstrap Integration**: Uses Bootstrap 4 for responsive layout.

3. **Cart Badge**: Navbar shows cart item count from `request.session.cart_items_count`.

4. **CSRF Protection**: Assumed present in forms (should be verified).

5. **No Template Tags**: No custom template tags or filters defined.

6. **JavaScript**: Inline JavaScript in checkout.html for shipping address toggle.

---

## 6. Configuration and Deployment

### 6.1 Django Settings

**File**: `webshop/settings.py`

**Key Configurations:**

- **SECRET_KEY**: Loaded from environment variable `DJANGO_SECRET_KEY`
- **DEBUG**: Loaded from environment variable `DEBUG` (default=0)
- **ALLOWED_HOSTS**: Should be configured (not visible in review)
- **DATABASE**: PostgreSQL configuration from environment
- **STATIC_FILES**: Collected via `collectstatic` in Docker
- **INSTALLED_APPS**: Includes shop app

**Environment Variables:**
- `DJANGO_SECRET_KEY`
- `DEBUG`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`

**Issue Identified by Ruff**: Import statement not at top of file (after docstring). This is actually acceptable but Ruff flags it.

### 6.2 Docker Configuration

#### Dockerfile

**Base Image**: python:3.13-slim

**Key Steps:**
1. Multi-stage build (not actually multi-stage, just single stage)
2. Install system dependencies (PostgreSQL client)
3. Copy requirements and install
4. Copy application code
5. **CRLF Fix**: `sed -i 's/\r$//' /app/init.sh` converts Windows line endings
6. Collect static files
7. Run init.sh script

**CMD**: `["/bin/bash", "/app/init.sh", "python", "manage.py", "runserver", "0.0.0.0:8000"]`

**Issues Fixed Previously:**
- CRLF line ending issue causing "no such file or directory" error
- Changed from ENTRYPOINT to CMD with bash wrapper

#### docker-compose.yml

**Services:**

1. **db**:
   - Image: postgres:17
   - Port: 5432
   - Environment: POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
   - Volume: postgres_data

2. **web**:
   - Build: .
   - Port: 8000:8000
   - Depends on: db
   - Environment: Django configuration
   - Volume: .:/app

**Network**: Default bridge network

#### init.sh

**Purpose**: Container startup script

**Logic:**
1. Wait for PostgreSQL connection (loop with timeout)
2. Run `makemigrations`
3. Run `migrate`
4. Create superuser if not exists (admin/1234)
5. Run `collectstatic --noinput`
6. Check if Product.objects.count() == 0
7. Load fixtures from `shop/fixtures/data.yaml` if empty
8. Execute remaining CMD arguments (runserver)

**Issues Fixed Previously:**
- CRLF line endings
- Path to fixtures (was my_shop, changed to shop)
- Smart fixture loading (only if database empty)

### 6.3 Deployment Observations

**Production Readiness Issues:**

1. **DEBUG Mode**: Currently enabled in development, must be False in production
2. **Secret Key**: Loaded from environment (correct)
3. **Allowed Hosts**: Must be configured for production
4. **Static Files**: Using Django's development server, should use nginx/Apache in production
5. **Database**: PostgreSQL in Docker (acceptable, but external managed DB recommended for production)
6. **HTTPS**: No SSL/TLS configuration visible
7. **Web Server**: Using Django's runserver (development only, should use gunicorn in production)
8. **Superuser Password**: Hardcoded as "1234" in init.sh (security risk)

---

## 7. Code Quality Analysis

### 7.1 Ruff Linter Results

**Scan Date**: December 10, 2025  
**Tool**: Ruff 0.14.8

**Issues Found**: 11 (5 auto-fixed, 6 remaining)

#### Auto-Fixed Issues (5):

1. **F811**: Redefinition of unused `Permission` in `create_roles_and_permissions.py:42`
   - Removed duplicate import

2-5. **F401**: Unused imports (4 instances)
   - `django.test.TestCase` in `shop/tests.py`
   - `django.shortcuts.render` in `shop/urls.py`
   - `django.db.IntegrityError` in `shop/views_login.py`
   - `django.shortcuts.redirect` in `shop/views_order.py`

#### Remaining Issues (6):

1-5. **E402**: Module level import not at top of file (5 instances in `create_roles_and_permissions.py`)
   - Lines 23, 29, 42, 53, 72
   - **Reason**: Script uses imports inline with Django shell commands
   - **Severity**: Low (not production code, just documentation/script)

6. **E402**: Module level import not at top of file in `webshop/settings.py:16`
   - **Reason**: Import after docstring (technically correct Django convention)
   - **Severity**: Very Low (false positive)

### 7.2 Code Structure Assessment

#### Positive Aspects:

1. **Separation of Concerns**: Views split into logical modules
2. **Model Documentation**: Good use of verbose_name and help_text
3. **Consistent Naming**: German translations consistently applied
4. **Method Encapsulation**: Models have helper methods (get_subtotal, is_in_stock)
5. **Validators**: Uses Django's built-in validators for constraints

#### Areas for Improvement:

1. **No Tests**: Empty tests.py file (only unused import)
2. **No Docstrings**: View functions lack docstrings
3. **No Type Hints**: Python 3.13 supports type hints, none used
4. **Manual Form Handling**: No Django Form classes
5. **No Service Layer**: Business logic mixed in views
6. **Hard-coded Strings**: Magic strings throughout views
7. **No Logging**: No logging configuration or usage
8. **No Error Pages**: No custom 404/500 templates mentioned

### 7.3 Structural Issues

#### File Organization:

1. **create_roles_and_permissions.py**: Placed in root instead of management command
   - Should be: `shop/management/commands/create_roles.py`
   - Current implementation is just documentation/script

2. **View Module Split**: Logical but could use deeper organization:
   ```
   shop/views/
   ├── __init__.py
   ├── product_views.py
   ├── cart_views.py
   ├── order_views.py
   ├── auth_views.py
   └── wishlist_views.py
   ```

3. **No Forms Module**: Form validation inline in views
   - Should be: `shop/forms.py` with Django Form classes

4. **No Services Module**: Business logic in views
   - Could benefit from: `shop/services/checkout_service.py`

#### Code Duplication:

1. **Authentication Check**: Repeated in multiple views
   ```python
   customer_id = request.session.get("customer_id")
   if not customer_id:
       messages.error(request, "Bitte logge dich ein")
       return redirect("login")
   ```
   - Should be: Custom decorator `@login_required_custom`

2. **Cart Count Update**: Repeated in 4 functions (cart_increase, cart_decrease, cart_remove, checkout)
   ```python
   total_items = sum(item.quantity for item in CartItem.objects.filter(cart=cart))
   request.session['cart_items_count'] = total_items
   ```
   - Should be: Helper function `update_cart_count(request, cart)`

3. **Stock Validation**: Repeated in add_to_cart and checkout
   - Should be: Model method or service function

#### Missing Abstractions:

1. **No Custom Managers**: Could benefit from custom QuerySets:
   ```python
   class OrderQuerySet(models.QuerySet):
       def for_customer(self, customer):
           return self.filter(customer=customer)
       
       def pending(self):
           return self.filter(status='pending')
   ```

2. **No Middleware**: Session-based auth could use middleware:
   ```python
   class CustomerAuthenticationMiddleware:
       def __init__(self, get_response):
           self.get_response = get_response
       
       def __call__(self, request):
           customer_id = request.session.get('customer_id')
           if customer_id:
               request.customer = Customer.objects.get(id=customer_id)
           else:
               request.customer = None
           return self.get_response(request)
   ```

---

## 8. Security Analysis

### 8.1 Identified Security Issues

#### Critical:

1. **Order Detail Authorization Missing** (views_order.py:10)
   - **Issue**: Any authenticated user can view any order by changing URL
   - **Impact**: Confidential order information disclosure
   - **Fix**: Add customer ownership check

2. **Checkout Stock Race Condition** (views_cart.py:122-145)
   - **Issue**: Stock check and decrement not atomic
   - **Impact**: Overselling of products
   - **Fix**: Use `select_for_update()` within transaction

3. **Hardcoded Superuser Password** (init.sh)
   - **Issue**: Admin password is "1234"
   - **Impact**: Unauthorized admin access
   - **Fix**: Generate random password or load from secure environment variable

#### High:

4. **No CSRF Verification Visible**
   - **Issue**: Not confirmed if CSRF tokens in templates
   - **Impact**: Cross-site request forgery attacks
   - **Status**: Needs template review

5. **Session Fixation Risk**
   - **Issue**: Session ID not rotated on login
   - **Impact**: Session hijacking
   - **Fix**: Add `request.session.cycle_key()` after login

#### Medium:

6. **No Rate Limiting**
   - **Issue**: No protection against brute force login attempts
   - **Impact**: Account compromise
   - **Fix**: Implement django-ratelimit or similar

7. **Email Enumeration** (views_login.py:72)
   - **Issue**: Different error messages for invalid email vs wrong password
   - **Impact**: User enumeration
   - **Fix**: Generic error message for both cases

8. **No Input Sanitization**
   - **Issue**: User input not explicitly sanitized
   - **Impact**: Potential XSS (mitigated by Django templates)
   - **Status**: Django provides automatic escaping, but should be verified

#### Low:

9. **No HTTPS Enforcement**
   - **Issue**: No secure cookie settings visible
   - **Impact**: Session cookie interception
   - **Fix**: Set SECURE_SSL_REDIRECT, SECURE_COOKIE_SECURE in settings

10. **No Content Security Policy**
    - **Issue**: No CSP headers
    - **Impact**: XSS attack surface
    - **Fix**: Implement django-csp

### 8.2 Security Best Practices Compliance

| Practice | Status | Notes |
|----------|--------|-------|
| Password Hashing | ✅ Pass | Uses Django's make_password (PBKDF2) |
| SQL Injection | ✅ Pass | Uses Django ORM (parameterized queries) |
| XSS Protection | ⚠️ Assumed | Django templates auto-escape, needs verification |
| CSRF Protection | ⚠️ Unknown | Not visible in code review |
| Session Security | ⚠️ Partial | Session used, but no rotation on login |
| Authorization | ❌ Fail | Order detail has no auth check |
| Input Validation | ⚠️ Partial | Some validation in views, no form classes |
| Secure Headers | ❌ Missing | No CSP, HSTS, X-Frame-Options visible |
| Rate Limiting | ❌ Missing | No rate limiting implemented |
| Audit Logging | ❌ Missing | No security event logging |

---

## 9. Performance Analysis

### 9.1 Database Query Patterns

#### Identified N+1 Queries:

1. **product_list** (views.py:10): Category relationship not preloaded
   ```python
   # Current:
   products = Product.objects.all()
   
   # Optimized:
   products = Product.objects.select_related('category').all()
   ```

2. **cart_view** (views_cart.py:14): Product relationships not preloaded
   ```python
   # Current:
   cart_items = CartItem.objects.filter(cart=cart)
   
   # Optimized:
   cart_items = CartItem.objects.filter(cart=cart).select_related('product')
   ```

3. **checkout** (views_cart.py:76): Product and order item relationships not optimized

#### Query Count Estimates (per page load):

| View | Queries (Current) | Queries (Optimized) | Improvement |
|------|------------------|---------------------|-------------|
| product_list | 1 + N (categories) | 2 | ~90% |
| cart_view | 3 + N (products) | 3 | ~80% |
| checkout (GET) | 3 + N (products) | 3 | ~80% |
| orders_list | 2 | 2 | 0% |
| order_detail | 2 + N (products) | 2 | ~85% |

### 9.2 Caching Opportunities

**High Impact:**

1. **Product List**: Cache product listings per filter combination
   ```python
   cache_key = f"products:{category_id}:{sort_by}:{page}"
   products = cache.get(cache_key)
   if not products:
       products = Product.objects.filter(...).all()
       cache.set(cache_key, products, 300)  # 5 min
   ```

2. **Category List**: Cache all categories (rarely changes)
   ```python
   categories = cache.get('categories')
   if not categories:
       categories = Category.objects.all()
       cache.set('categories', categories, 3600)  # 1 hour
   ```

3. **Cart Count**: Already cached in session (efficient)

**Medium Impact:**

4. **Order History**: Cache per customer
5. **Product Detail**: Cache individual products

### 9.3 Database Indexing

**Recommended Indexes:**

```python
class Product(models.Model):
    # ...
    class Meta:
        indexes = [
            models.Index(fields=['category', 'price']),  # Filter queries
            models.Index(fields=['name']),               # Search queries
            models.Index(fields=['-stock']),             # Low stock queries
        ]

class Order(models.Model):
    # ...
    class Meta:
        indexes = [
            models.Index(fields=['customer', '-order_date']),  # Customer orders
            models.Index(fields=['status', '-order_date']),    # Admin dashboard
        ]
```

### 9.4 Performance Bottlenecks

1. **Checkout Transaction**: 10+ database operations without connection pooling
2. **Cart Total Calculation**: Calculated in Python instead of SQL aggregation
3. **No Pagination**: Product list and order history can grow unbounded
4. **Image Processing**: No thumbnail generation or lazy loading
5. **Static Files**: Served by Django in development (acceptable, use CDN in production)

---

## 10. Testing Coverage

### 10.1 Current Test Status

**File**: `shop/tests.py`

```python
from django.test import TestCase

# Create your tests here.
```

**Status**: ❌ No tests implemented

**Coverage**: 0%

### 10.2 Recommended Test Structure

```
shop/tests/
├── __init__.py
├── test_models.py          # Model method tests
├── test_views.py           # View integration tests
├── test_forms.py           # Form validation tests
├── test_authentication.py  # Login/register tests
├── test_cart.py            # Cart operations tests
├── test_checkout.py        # Checkout process tests
└── test_security.py        # Authorization tests
```

### 10.3 Critical Test Cases Needed

#### Model Tests:
- Customer password hashing and verification
- Product stock validation
- Order total calculation
- Address string representation

#### View Tests:
- Authentication requirement enforcement
- Order detail authorization
- Cart stock validation
- Checkout transaction atomicity

#### Integration Tests:
- Complete purchase flow
- Cart persistence across sessions
- Stock decrement on purchase
- Payment and shipment creation

---

## 11. Recommendations

### 11.1 Critical Priority (Security & Data Integrity)

1. **Fix Order Detail Authorization**
   ```python
   def order_detail(request, order_id):
       customer_id = request.session.get("customer_id")
       if not customer_id:
           return redirect("login")
       order = get_object_or_404(Order, id=order_id, customer_id=customer_id)
       # ...
   ```

2. **Implement Atomic Checkout**
   ```python
   from django.db import transaction
   
   @transaction.atomic
   def checkout(request):
       # Lock products for update
       for item in cart_items:
           product = Product.objects.select_for_update().get(id=item.product.id)
           # ...
   ```

3. **Secure Superuser Password**: Remove hardcoded password from init.sh

4. **Add Session Rotation**: Call `request.session.cycle_key()` after login

### 11.2 High Priority (Code Quality)

5. **Implement Django Forms**
   ```python
   # shop/forms.py
   class CheckoutForm(forms.Form):
       billing_street = forms.CharField(max_length=100)
       # ...
   ```

6. **Add Authentication Decorator**
   ```python
   def customer_login_required(view_func):
       def wrapper(request, *args, **kwargs):
           if not request.session.get("customer_id"):
               return redirect("login")
           return view_func(request, *args, **kwargs)
       return wrapper
   ```

7. **Extract Duplicate Code**: Create helper functions for cart count update, auth check

8. **Add Comprehensive Tests**: Minimum 60% coverage target

### 11.3 Medium Priority (Performance)

9. **Add select_related/prefetch_related**: Optimize N+1 queries

10. **Implement Pagination**: Use Django's Paginator for product list and orders

11. **Add Database Indexes**: See section 9.3

12. **Implement Caching**: Cache category list, product listings

### 11.4 Low Priority (Architecture)

13. **Create Service Layer**: Extract business logic from views

14. **Add Custom Managers**: Create reusable QuerySet methods

15. **Implement Middleware**: Handle customer authentication globally

16. **Add Management Commands**: Convert create_roles_and_permissions.py to proper command

---

## 12. Conclusion

### 12.1 System Overview

The webshop application is a **functional e-commerce platform** with core features implemented correctly. The codebase demonstrates understanding of Django fundamentals and follows many best practices for model design and view structure.

### 12.2 Strengths

1. **Well-structured Models**: 11 models with proper relationships and validators
2. **Separation of Concerns**: Views logically separated into 6 modules
3. **German Localization**: Consistent use of German verbose names
4. **Docker Integration**: Containerized deployment with PostgreSQL
5. **Session Management**: Effective use of sessions for cart state

### 12.3 Critical Weaknesses

1. **Security Vulnerabilities**: Order detail authorization missing, checkout race condition
2. **No Tests**: 0% test coverage
3. **Performance Issues**: N+1 queries, no caching, no pagination
4. **Code Duplication**: Auth checks, cart count updates repeated
5. **Missing Abstractions**: No forms, service layer, or middleware

### 12.4 Production Readiness: ⚠️ Not Ready

**Blockers:**
- Critical security issues must be resolved
- Tests must be implemented
- Checkout transaction must be made atomic
- Performance optimizations needed for scale

**Estimated Work to Production:**
- Security fixes: 1-2 days
- Test suite: 3-5 days
- Performance optimization: 2-3 days
- **Total**: ~2 weeks

### 12.5 Overall Assessment

**Grade**: C+ (Functional but needs significant improvement)

The application successfully implements e-commerce functionality and demonstrates solid Django fundamentals. However, security vulnerabilities, lack of tests, and performance issues prevent production deployment. With focused effort on the critical issues identified in this document, the system can be brought to production quality.

---

## Appendix A: File Metrics

| File | Lines | Functions/Classes | Complexity |
|------|-------|------------------|------------|
| models.py | 429 | 12 classes | Medium |
| views_cart.py | 168 | 5 functions | High |
| views.py | ~94 | 3 functions | Medium |
| views_login.py | ~94 | 3 functions | Medium |
| views_order.py | ~14 | 2 functions | Low |
| views_product.py | ~7 | 1 function | Low |
| views_wishlist.py | ~33 | 2 functions | Low |
| urls.py | ~22 | 16 URL patterns | Low |
| admin.py | ~5 | 1 registration | Low |
| settings.py | 139 | 0 | Low |

**Total Python Code**: ~1,005 lines (excluding migrations, tests, fixtures)

---

## Appendix B: Dependency Analysis

**File**: `requirements.txt`

Key dependencies (versions should be verified):
- Django==5.2.8
- psycopg2-binary (PostgreSQL adapter)
- gunicorn (WSGI server)
- python-dotenv (environment variables)
- Pillow (image handling)

---

*End of Technical Documentation*





Basierend auf den Bewertungskriterien und eurem aktuellen Stand:

✅ Was ihr habt (20/50 Punkte gesichert):
Scrum-Board & Rollenverteilung (5 Punkte) ✅
Angebotsvergleich (5 Punkte) ✅
DB-Schnittstelle vorgestellt (5 Punkte) ✅
DB-Technologie begründet (5 Punkte) ✅
⚠️ Was noch fehlt/verbessert werden muss (30/50 Punkte):
5. Datenmodell entwickelt, dokumentiert und dargestellt (5 Punkte)
Status: ⚠️ TEILWEISE - Ihr habt das Modell, aber Dokumentation unvollständig

Was ihr habt:

✅ 12 Models in models.py (429 Zeilen)
✅ Technische Dokumentation gerade erstellt
Was noch fehlt:

📊 Entity-Relationship-Diagramm (ERD) - visuell!
📄 Dokumentation sollte für Präsentation aufbereitet werden
Schnelle Lösung:

Oder online Tool: dbdiagram.io - 15 Minuten Arbeit

6. Realisierung der Anwendung (10 Punkte)
Status: ⚠️ KRITISCH - 6/10 Punkte gefährdet

Was funktioniert:

✅ Webshop läuft in Docker
✅ Produktliste, Warenkorb, Checkout
✅ Login/Register
✅ Bestellungen, Wishlist
✅ Session-basierte Authentifizierung
Kritische Probleme aus der Dokumentation:

Sicherheitslücke: order_detail hat keine Autorisierung

❌ Jeder User kann jede Bestellung sehen!
Muss vor Präsentation gefixt werden
Race Condition: Checkout nicht atomar

⚠️ Kann zu Überverkäufen führen
Sollte gefixt werden
Keine Tests: 0% Coverage

⚠️ Könnte Punktabzug geben
Empfehlung:

JETZT sofort fixen: Order Detail Security (10 Minuten)
Optional: Checkout atomic (30 Minuten)
Bei Zeit: Basis-Tests schreiben (1-2 Stunden)
7. Präsentation (15 Punkte)
Status: ❓ UNKLAR - Größter Punkteblock!

Struktur für 25 Minuten:

Intro (2 min): Projekt-Überblick, Team-Vorstellung
Scrum-Prozess (3 min): Board zeigen, Sprints, Rollen
Anforderungsanalyse (2 min): Angebotsvergleich
Datenmodell (4 min): ERD zeigen, Models erklären
Technologie-Stack (4 min): Django/PostgreSQL/Docker Begründung
Live-Demo (7 min): Durchklicken (Register → Produkte → Warenkorb → Checkout → Bestellung)
Code-Highlights (2 min): Wichtige Views/Models kurz zeigen
Fazit (1 min): Lessons learned
Kritische Punkte:

🎯 Jedes Mitglied muss sprechen - Teile aufteilen!
📊 Visualisierung: ERD, Screenshots, Scrum-Board
🔴 Roter Faden: Story erzählen, nicht nur Features auflisten
⏱️ Timing: Proben! 25 Min einhalten
🎯 Meine Empfehlung für maximale Punkte:
Sofort (heute, 1-2 Stunden):
✅ Security-Fix für order_detail (10 min)
✅ Checkout atomic machen (30 min)
📊 ERD erstellen (15 min)
📋 Präsentations-Outline schreiben und Rollen verteilen (30 min)
Diese Woche:
🧪 Basis-Tests schreiben (2-3 Stunden)
🎤 Präsentation 2x durchproben mit Zeitmessung
Realistisches Ziel:
Mit Fixes: 45-48/50 Punkte möglich
Ohne Fixes: 38-42/50 Punkte Risiko
Soll ich die kritischen Security-Fixes jetzt direkt umsetzen? Das würde eure "Realisierung der Anwendung"-Punkte absichern und dauert nur 15 Minuten.