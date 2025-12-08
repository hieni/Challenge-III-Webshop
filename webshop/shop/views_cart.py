from django.shortcuts import render, redirect
from django.contrib import messages
from decimal import Decimal
from .models import Customer, Cart, CartItem, Order, OrderItem

def cart_view(request):
    customer_id = request.session.get("customer_id")
    if not customer_id:
        messages.error(request, "Bitte logge dich ein, um deinen Warenkorb zu sehen.")
        return redirect("product_list")

    customer = Customer.objects.get(id=customer_id)
    cart, _ = Cart.objects.get_or_create(customer=customer)
    cart_items = CartItem.objects.filter(cart=cart)

    for item in cart_items:
        item.total_price = item.product.price * item.quantity

    total_price = sum(item.total_price for item in cart_items)

    context = {
        "cart_items": cart_items,
        "total_price": total_price,
    }
    return render(request, "cart.html", context)

def cart_increase(request, item_id):
    cart_item = CartItem.objects.get(id=item_id)
    
    if cart_item.quantity >= cart_item.product.stock:
        messages.error(request, f"Nicht genug Bestand für {cart_item.product.name}.")
        return redirect("cart")
    else: 
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, "Menge erhöht.")
        return redirect("cart")

def cart_decrease(request, item_id):
    cart_item = CartItem.objects.get(id=item_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    messages.info(request, "Menge aktualisiert.")
    return redirect("cart")

def cart_remove(request, item_id):
    cart_item = CartItem.objects.get(id=item_id)
    cart_item.delete()
    messages.warning(request, "Artikel entfernt.")
    return redirect("cart")

def checkout(request):
    customer_id = request.session.get("customer_id")
    if not customer_id:
        messages.error(request, "Bitte einloggen.")
        return redirect("login")

    customer = Customer.objects.get(id=customer_id)
    cart = Cart.objects.get(customer=customer)
    cart_items = CartItem.objects.filter(cart=cart)
    
    # Prüfen ob in Stock
    for item in cart_items:
        if item.quantity > item.product.stock:
            messages.error(request, f"Nicht genug Bestand für {item.product.name}.")
            return redirect("cart")

    if not cart_items:
        messages.error(request, "Dein Warenkorb ist leer.")
        return redirect("cart")

    total = sum(item.product.price * item.quantity for item in cart_items)

    order = Order.objects.create(
        customer=customer,
        status="Bestellt",
        total_amount=Decimal(total)
    )

    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price_per_unit=item.product.price
        )
        product = item.product
        product.stock -= item.quantity
        product.save()

    cart_items.delete()

    messages.success(request, "Bestellung erfolgreich!")
    return redirect("order_detail", order_id=order.id)
