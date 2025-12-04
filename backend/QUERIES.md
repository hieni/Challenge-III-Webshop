# Webshop Django ORM Queries

This document contains example ORM queries for the webshop application.

## Setup & Running

### Start Docker Services
```powershell
cd webshop
docker compose up -d
```

### Run Migrations
```powershell
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
```

### Load Sample Data
```powershell
docker compose exec web python manage.py load_sample_data
```

### Create Superuser
```powershell
docker compose exec web python manage.py createsuperuser
```

### Access Admin Panel
http://localhost:8000/admin/

## API Endpoints

All endpoints return JSON data:

- `GET /shop/api/products/` - All products with categories
- `GET /shop/api/customer/<id>/orders/` - Customer's orders
- `GET /shop/api/order/<id>/` - Order details with items
- `GET /shop/api/customer/<id>/cart/` - Customer's cart
- `GET /shop/api/bestsellers/` - Best selling products
- `GET /shop/api/low-stock/` - Products with stock < 10
- `GET /shop/api/customer-stats/` - Customer statistics
- `GET /shop/api/category-stats/` - Category statistics

## Example ORM Queries

### Basic Queries

```python
from shop.models import Customer, Category, Product, Order, OrderItem, Cart, CartItem

# Get all products
products = Product.objects.all()

# Get products with category
products = Product.objects.select_related('category').all()

# Get single product
product = Product.objects.get(product_id=1)

# Filter products by category
electronics = Product.objects.filter(category__category_name='Electronics')

# Filter by price range
affordable = Product.objects.filter(price__lte=100)
expensive = Product.objects.filter(price__gte=500)
mid_range = Product.objects.filter(price__range=(100, 500))

# Search products by name
products = Product.objects.filter(name__icontains='computer')
```

### Relationships

```python
# Get all products in a category
category = Category.objects.get(category_name='Electronics')
products = category.products.all()

# Get customer's orders
customer = Customer.objects.get(email='deborah.bruen@example.com')
orders = customer.orders.all()

# Get order items for an order
order = Order.objects.get(order_id=1)
items = order.items.select_related('product').all()

# Get customer's cart
cart = customer.cart
cart_items = cart.items.select_related('product').all()
```

### Aggregations

```python
from django.db.models import Sum, Count, Avg, F

# Total revenue per product
products = Product.objects.annotate(
    total_sold=Sum('order_items__quantity'),
    revenue=Sum(F('order_items__quantity') * F('order_items__price_per_unit'))
)

# Customer order statistics
customers = Customer.objects.annotate(
    order_count=Count('orders'),
    total_spent=Sum('orders__total_amount')
).order_by('-total_spent')

# Category product counts
categories = Category.objects.annotate(
    product_count=Count('products'),
    total_stock=Sum('products__stock')
)

# Average order value
from django.db.models import Avg
avg_order = Order.objects.aggregate(avg_amount=Avg('total_amount'))

# Products with low stock
low_stock = Product.objects.filter(stock__lt=10).count()
```

### Complex Queries

```python
from django.db.models import Q, F, Sum

# Products that are in stock OR price less than 100
products = Product.objects.filter(
    Q(stock__gt=0) | Q(price__lt=100)
)

# Customers who spent more than 500
big_spenders = Customer.objects.annotate(
    total=Sum('orders__total_amount')
).filter(total__gt=500)

# Orders from last 30 days
from datetime import datetime, timedelta
recent_orders = Order.objects.filter(
    order_date__gte=datetime.now().date() - timedelta(days=30)
)

# Products never ordered
never_ordered = Product.objects.filter(order_items__isnull=True)

# Most expensive product per category
from django.db.models import Max
expensive_by_category = Product.objects.values('category__category_name').annotate(
    max_price=Max('price')
)
```

### Ordering

```python
# Order by price ascending
products = Product.objects.order_by('price')

# Order by price descending
products = Product.objects.order_by('-price')

# Order by multiple fields
products = Product.objects.order_by('category__category_name', '-price')

# Order by annotation
bestsellers = Product.objects.annotate(
    total_sold=Sum('order_items__quantity')
).order_by('-total_sold')
```

### Creating & Updating

```python
# Create a new customer
customer = Customer.objects.create(
    first_name='John',
    last_name='Doe',
    email='john.doe@example.com',
    password='hashed_password',
    strasse='123 Main St',
    ort='Springfield',
    plz='12345'
)

# Update product stock
product = Product.objects.get(product_id=1)
product.stock = 100
product.save()

# Bulk update
Product.objects.filter(category__category_name='Electronics').update(
    stock=F('stock') + 10
)

# Add item to cart
cart = Cart.objects.get(customer=customer)
CartItem.objects.create(
    cart=cart,
    product=product,
    quantity=2
)
```

### Deleting

```python
# Delete a cart item
cart_item = CartItem.objects.get(cart_item_id=1)
cart_item.delete()

# Delete all orders older than 1 year
from datetime import datetime, timedelta
old_date = datetime.now().date() - timedelta(days=365)
Order.objects.filter(order_date__lt=old_date).delete()
```

### Transactions

```python
from django.db import transaction

# Create order with items atomically
with transaction.atomic():
    order = Order.objects.create(
        customer=customer,
        status='pending',
        total_amount=0
    )
    
    total = 0
    for cart_item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            quantity=cart_item.quantity,
            price_per_unit=cart_item.product.price
        )
        total += cart_item.quantity * cart_item.product.price
        
        # Update stock
        cart_item.product.stock -= cart_item.quantity
        cart_item.product.save()
    
    order.total_amount = total
    order.save()
    
    # Clear cart
    cart.items.all().delete()
```

### Raw SQL (when ORM isn't enough)

```python
# Execute raw SQL
products = Product.objects.raw(
    'SELECT * FROM product WHERE stock > %s',
    [10]
)

# Direct SQL execution
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("SELECT COUNT(*) FROM product WHERE stock < 10")
    row = cursor.fetchone()
    print(f"Low stock products: {row[0]}")
```

## Testing Queries in Django Shell

```powershell
docker compose exec web python manage.py shell
```

Then in the shell:
```python
from shop.models import *
from django.db.models import Sum, Count, F, Q

# Try your queries here
products = Product.objects.all()
for p in products[:5]:
    print(f"{p.name}: ${p.price}")
```
