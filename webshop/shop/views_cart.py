from django.shortcuts import render, redirect
from django.contrib import messages
from decimal import Decimal
from .models import Customer, Cart, CartItem, Order, OrderItem, Address, Payment, Shipment

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
        
        # Update session cart count
        total_items = sum(item.quantity for item in CartItem.objects.filter(cart=cart_item.cart))
        request.session['cart_items_count'] = total_items
        
        messages.success(request, "Menge erhöht.")
        return redirect("cart")

def cart_decrease(request, item_id):
    cart_item = CartItem.objects.get(id=item_id)
    cart = cart_item.cart
    
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    
    # Update session cart count
    total_items = sum(item.quantity for item in CartItem.objects.filter(cart=cart))
    request.session['cart_items_count'] = total_items
    
    messages.info(request, "Menge aktualisiert.")
    return redirect("cart")

def cart_remove(request, item_id):
    cart_item = CartItem.objects.get(id=item_id)
    cart = cart_item.cart
    cart_item.delete()
    
    # Update session cart count
    total_items = sum(item.quantity for item in CartItem.objects.filter(cart=cart))
    request.session['cart_items_count'] = total_items
    
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

    if not cart_items:
        messages.error(request, "Dein Warenkorb ist leer.")
        return redirect("cart")

    # Prüfen ob in Stock
    for item in cart_items:
        if item.quantity > item.product.stock:
            messages.error(request, f"Nicht genug Bestand für {item.product.name}.")
            return redirect("cart")

    # Calculate total for both GET and POST
    for item in cart_items:
        item.total_price = item.product.price * item.quantity
    total_price = sum(item.total_price for item in cart_items)

    if request.method == "POST":
        same_as_billing = request.POST.get("same_as_billing") == "on"

        # Rechnungsadresse erstellen
        billing_address = Address.objects.create(
            customer=customer,
            street=request.POST.get("billing_street"),
            city=request.POST.get("billing_city"),
            postal_code=request.POST.get("billing_postal_code"),
            country=request.POST.get("billing_country", "Germany")
        )

        # Lieferadresse
        if same_as_billing:
            shipment_address = billing_address
        else:
            shipment_address = Address.objects.create(
                customer=customer,
                street=request.POST.get("shipping_street"),
                city=request.POST.get("shipping_city"),
                postal_code=request.POST.get("shipping_postal_code"),
                country=request.POST.get("shipping_country", "Germany")
            )

        # Bestellung erstellen
        order = Order.objects.create(
            customer=customer,
            status="pending",
            total_amount=Decimal(str(total_price)),
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

        # Payment und Shipment erstellen
        Payment.objects.create(
            order=order,
            amount=order.total_amount,
            payment_method=request.POST.get("payment_method", "invoice"),
            status="pending"
        )
        
        Shipment.objects.create(
            order=order,
            status="pending"
        )

        cart_items.delete()
        
        # Reset cart count in session
        request.session['cart_items_count'] = 0
        
        messages.success(request, "Bestellung erfolgreich!")
        return redirect("order_detail", order_id=order.id)
    
    # GET request - show checkout form
    # Pre-fill with default billing address if exists
    default_address = customer.default_billing_address
    
    return render(request, "checkout.html", {
        "customer": customer,
        "cart_items": cart_items,
        "total_price": total_price,
        "default_address": default_address,
    })