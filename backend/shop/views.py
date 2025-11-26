from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Sum, Count, F, Q
from .models import Customer, Category, Product, Order, OrderItem, Cart, CartItem


def products_with_categories(request):
    """Get all products with their category names"""
    products = Product.objects.select_related('category').all()
    data = [{
        'product_id': p.product_id,
        'name': p.name,
        'price': str(p.price),
        'stock': p.stock,
        'category': p.category.category_name
    } for p in products]
    return JsonResponse(data, safe=False)


def customer_orders(request, customer_id):
    """Get all orders for a specific customer"""
    orders = Order.objects.filter(customer_id=customer_id).select_related('customer')
    data = [{
        'order_id': o.order_id,
        'order_date': o.order_date.isoformat(),
        'status': o.status,
        'total_amount': str(o.total_amount),
        'customer_email': o.customer.email
    } for o in orders]
    return JsonResponse(data, safe=False)


def order_details(request, order_id):
    """Get order details with all items"""
    items = OrderItem.objects.filter(order_id=order_id).select_related(
        'order', 'order__customer', 'product'
    )
    data = [{
        'order_id': item.order.order_id,
        'order_date': item.order.order_date.isoformat(),
        'customer_name': f"{item.order.customer.first_name} {item.order.customer.last_name}",
        'product_name': item.product.name,
        'quantity': item.quantity,
        'price_per_unit': str(item.price_per_unit),
        'subtotal': str(item.subtotal)
    } for item in items]
    return JsonResponse(data, safe=False)


def cart_contents(request, customer_id):
    """Get cart contents for a specific customer"""
    try:
        cart = Cart.objects.get(customer_id=customer_id)
        items = CartItem.objects.filter(cart=cart).select_related('product')
        data = {
            'customer_id': customer_id,
            'items': [{
                'product_name': item.product.name,
                'price': str(item.product.price),
                'quantity': item.quantity,
                'subtotal': str(item.subtotal)
            } for item in items],
            'total': str(cart.total)
        }
        return JsonResponse(data)
    except Cart.DoesNotExist:
        return JsonResponse({'error': 'Cart not found'}, status=404)


def bestselling_products(request):
    """Get best selling products"""
    products = Product.objects.annotate(
        total_sold=Sum('order_items__quantity'),
        total_revenue=Sum(F('order_items__quantity') * F('order_items__price_per_unit'))
    ).filter(total_sold__isnull=False).order_by('-total_sold')[:10]
    
    data = [{
        'product_id': p.product_id,
        'name': p.name,
        'price': str(p.price),
        'total_sold': p.total_sold or 0,
        'total_revenue': str(p.total_revenue or 0)
    } for p in products]
    return JsonResponse(data, safe=False)


def low_stock_products(request):
    """Get products with low stock (less than 10)"""
    products = Product.objects.filter(stock__lt=10).select_related('category')
    data = [{
        'product_id': p.product_id,
        'name': p.name,
        'price': str(p.price),
        'stock': p.stock,
        'category': p.category.category_name
    } for p in products]
    return JsonResponse(data, safe=False)


def customer_stats(request):
    """Get customer order statistics"""
    customers = Customer.objects.annotate(
        total_orders=Count('orders'),
        total_spent=Sum('orders__total_amount')
    ).order_by('-total_spent')
    
    data = [{
        'customer_id': c.customer_id,
        'name': f"{c.first_name} {c.last_name}",
        'email': c.email,
        'total_orders': c.total_orders or 0,
        'total_spent': str(c.total_spent or 0)
    } for c in customers]
    return JsonResponse(data, safe=False)


def categories_stats(request):
    """Get product count by category"""
    categories = Category.objects.annotate(
        product_count=Count('products'),
        total_stock=Sum('products__stock'),
        avg_price=Sum('products__price') / Count('products')
    )
    
    data = [{
        'category_name': c.category_name,
        'product_count': c.product_count or 0,
        'total_stock': c.total_stock or 0,
        'avg_price': str(c.avg_price or 0) if c.avg_price else '0.00'
    } for c in categories]
    return JsonResponse(data, safe=False)
