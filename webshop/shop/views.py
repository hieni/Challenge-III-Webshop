from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product, Customer, Cart, CartItem

def home(request):
    return render(request, "home.html")

def product_list(request):
    products = Product.objects.all()
    return render(request, "products.html", {"products": products})

def add_to_cart(request, product_id):
    customer_id = request.session.get("customer_id")
    if not customer_id:
        messages.error(request, "Bitte logge dich ein, um Artikel zum Warenkorb hinzuzufügen.")
        return redirect("product_list")

    customer = Customer.objects.get(id=customer_id)
    product = get_object_or_404(Product, id=product_id)

    if product.stock <= 0:
        messages.error(request, "Dieses Produkt ist leider ausverkauft.")
        return redirect("product_list")
    
    cart, _ = Cart.objects.get_or_create(customer=customer)

    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={"quantity": 1}
    )
    
    if not item_created and not cart_item.quantity >= cart_item.product.stock:
        cart_item.quantity += 1
        cart_item.save()
    else: 
        messages.error(request, f"Nicht genug Bestand für {cart_item.product.name}.")
        return redirect("product_list")

    total_items = sum(item.quantity for item in CartItem.objects.filter(cart=cart))
    request.session['cart_items_count'] = total_items

    messages.success(request, f"{product.name} wurde in den Warenkorb gelegt.")
    return redirect("product_list")
