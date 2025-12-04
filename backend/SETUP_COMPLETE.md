# Django Webshop - Fully Automated Setup! 🚀

## One-Command Setup

Just run:
```powershell
docker compose up -d
```

That's it! Everything is automatically configured:
- ✅ Database migrations
- ✅ Superuser creation (admin/admin123)
- ✅ Sample data loaded
- ✅ Server started

## What's Running

- **PostgreSQL Database**: `localhost:5432`
- **Django Application**: `http://localhost:8000`
- **Admin Panel**: `http://localhost:8000/admin/`
  - Username: `admin`
  - Password: `admin123`

## Created Components

### Django ORM Models (shop/models.py)
All models match your ER diagram:
- ✅ **Customer** - Customer data with address
- ✅ **Category** - Product categories
- ✅ **Product** - Products with category relationship
- ✅ **Order** - Customer orders
- ✅ **OrderItem** - Order line items (many-to-many junction)
- ✅ **Cart** - Shopping cart (one-to-one with customer)
- ✅ **CartItem** - Cart items (many-to-many junction)

### API Endpoints (shop/urls.py)
All endpoints return JSON:

```
GET /shop/api/products/                    - All products with categories
GET /shop/api/customer/<id>/orders/        - Customer's orders
GET /shop/api/order/<id>/                  - Order details with items
GET /shop/api/customer/<id>/cart/          - Customer's cart contents
GET /shop/api/bestsellers/                 - Best selling products
GET /shop/api/low-stock/                   - Products with stock < 10
GET /shop/api/customer-stats/              - Customer order statistics
GET /shop/api/category-stats/              - Category statistics
```

### Sample Data Loaded
- ✅ 22 Categories
- ✅ 5 Customers
- ✅ 10 Products
- ✅ 1 Order with items
- ✅ 1 Cart with items

### Admin Interface
Full CRUD operations available at `/admin/` for:
- Customers, Categories, Products
- Orders (with inline order items)
- Carts (with inline cart items)

## Quick Start Commands

### View Logs
```powershell
docker compose logs -f web
```

### Django Shell (Test ORM Queries)
```powershell
docker compose exec web python manage.py shell
```

Example queries in shell:
```python
from shop.models import *
from django.db.models import Sum, Count, F

# Get all products
Product.objects.all()

# Products with category
Product.objects.select_related('category').all()

# Customer's orders
Customer.objects.get(customer_id=1).orders.all()

# Bestsellers
Product.objects.annotate(
    total_sold=Sum('order_items__quantity')
).order_by('-total_sold')
```

### Restart Services
```powershell
docker compose restart
```

### Stop Services
```powershell
docker compose down
```

## Test the APIs

```powershell
# All products
curl http://localhost:8000/shop/api/products/

# Customer 1's orders
curl http://localhost:8000/shop/api/customer/1/orders/

# Order details
curl http://localhost:8000/shop/api/order/1/

# Customer 1's cart
curl http://localhost:8000/shop/api/customer/1/cart/

# Bestsellers
curl http://localhost:8000/shop/api/bestsellers/

# Low stock products
curl http://localhost:8000/shop/api/low-stock/

# Customer statistics
curl http://localhost:8000/shop/api/customer-stats/

# Category statistics
curl http://localhost:8000/shop/api/category-stats/
```

## Documentation

See `QUERIES.md` for comprehensive Django ORM examples including:
- Basic queries and filtering
- Relationships and joins
- Aggregations and annotations
- Complex queries with Q objects
- Creating, updating, deleting
- Transactions
- Raw SQL when needed

## Database Schema

All tables use the exact field names from your ER diagram:
- Primary keys: `customer_id`, `product_id`, `order_id`, etc.
- Foreign keys properly configured with CASCADE/RESTRICT
- Indexes on all foreign keys for performance
- Unique constraints (e.g., `cart_id + product_id`)

## Next Steps

1. **Explore the Admin Panel**: http://localhost:8000/admin/
2. **Try the API endpoints** with curl or browser
3. **Open Django Shell** and test ORM queries
4. **Check QUERIES.md** for comprehensive examples
5. **Add more data** via admin or `load_sample_data` command

Everything is ready to work! 🚀
