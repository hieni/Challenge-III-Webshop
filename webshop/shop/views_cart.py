from django.shortcuts import render, redirect
from django.contrib import messages
from decimal import Decimal
from .models import Customer, Cart, CartItem, Order, OrderItem, Address

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

def checkout_page(request):
    customer_id = request.session.get("customer_id")
    if not customer_id:
        messages.error(request, "Bitte einloggen.")
        return redirect("login")

    customer = Customer.objects.get(id=customer_id)
    cart = Cart.objects.get(customer=customer)
    cart_items = CartItem.objects.filter(cart=cart)
    
    if not cart_items:
        messages.error(request, "Dein Warenkorb ist leer.")
        return redirect("cart")

    # Prüfen Lagerbestand
    for item in cart_items:
        if item.quantity > item.product.stock:
            messages.error(request, f"Nicht genug Bestand für {item.product.name}.")
            return redirect("cart")
    
    return render(request, "checkout.html", {
        "cart_items": cart_items,
        "customer": customer,
        "total_price": sum(item.product.price * item.quantity for item in cart_items)
    })    

def checkout(request):
    customer_id = request.session.get("customer_id")
    if not customer_id:
        messages.error(request, "Bitte einloggen.")
        return redirect("login")

    customer = Customer.objects.get(id=customer_id)
    cart = Cart.objects.get(customer=customer)
    cart_items = CartItem.objects.filter(cart=cart)

    if not cart_items:
        messages.error(request, "Dein Warenkorb ist leer.")
        return redirect("cart")

    # Prüfen Lagerbestand
    for item in cart_items:
        if item.quantity > item.product.stock:
            messages.error(request, f"Nicht genug Bestand für {item.product.name}.")
            return redirect("cart")

    if request.method == "POST":
        use_existing_billing = request.POST.get("use_existing_billing") == "on"
        shipping_same_as_billing = request.POST.get("shipping_same_as_billing") == "on"
        set_default_billing = request.POST.get("set_default_billing") == "on"
        set_default_shipping = request.POST.get("set_default_shipping") == "on"

        # Rechnungsadresse
        if use_existing_billing and customer.default_billing_address:
            billing_address = customer.default_billing_address
        else:
            billing_address = Address.objects.create(
                customer=customer,
                street=request.POST.get("billing_street"),
                city=request.POST.get("billing_city"),
                postal_code=request.POST.get("billing_postal_code"),
                country="Deutschland"  # optional anpassen
            )
            if set_default_billing:
                customer.default_billing_address = billing_address
                customer.save()

        # Lieferadresse
        if shipping_same_as_billing:
            shipment_address = billing_address
        else:
            shipment_address = Address.objects.create(
                customer=customer,
                street=request.POST.get("shipping_street"),
                city=request.POST.get("shipping_city"),
                postal_code=request.POST.get("shipping_postal_code"),
                country="Deutschland"
            )
            if set_default_shipping:
                customer.default_shipping_address = shipment_address
                customer.save()

        # Bestellung erstellen
        total = sum(item.product.price * item.quantity for item in cart_items)
        order = Order.objects.create(
            customer=customer,
            status="Bestellt",
            billing_address=billing_address,
            shipment_address=shipment_address
        )

        # OrderItems und Lagerbestand aktualisieren
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price_per_unit=item.product.price
            )
            item.product.stock -= item.quantity
            item.product.save()

        cart_items.delete()
        
        messages.success(request, "Bestellung erfolgreich!")
        return redirect("order_detail", order_id=order.id)