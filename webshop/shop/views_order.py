from django.shortcuts import render
from .models import Order, OrderItem, Customer

def orders_list(request):
    customer_id = request.session.get("customer_id")
    customer = Customer.objects.get(id=customer_id)
    orders = Order.objects.filter(customer=customer).order_by("-order_date")
    return render(request, "orders.html", {"orders": orders})

def order_detail(request, order_id):
    order = Order.objects.get(id=order_id)
    items = OrderItem.objects.filter(order=order)
    return render(request, "order_detail.html", {"order": order, "items": items})
