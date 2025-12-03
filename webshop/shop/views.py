from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product, Customer, Cart, CartItem

def home(request):
    return render(request, "home.html")

def product_list(request):
    products = Product.objects.all()
    return render(request, "products.html", {"products": products})

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            customer = Customer.objects.get(email=email)
        except Customer.DoesNotExist:
            messages.error(request, "Benutzer existiert nicht.")
            return redirect("login")
        
        if customer.check_password(password):
            request.session["customer_id"] = customer.id
            messages.success(request, f"Willkommen zurück, {customer.first_name}!")
            return redirect("product_list")
        else:
            messages.error(request, "Falsches Passwort.")
            return redirect("login")

    return render(request, "login.html")


def logout_view(request):
    request.session.flush()
    messages.info(request, "Du wurdest ausgeloggt.")
    return redirect("login")

def add_to_cart(request, product_id):
    customer_id = request.session.get("customer_id")
    if not customer_id:
        messages.error(request, "Bitte logge dich ein, um Artikel zum Warenkorb hinzuzufügen.")
        return redirect("product_list")

    customer = Customer.objects.get(id=customer_id)
    product = get_object_or_404(Product, id=product_id)

    cart, _ = Cart.objects.get_or_create(customer=customer)

    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={"quantity": 1}
    )

    if not item_created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f"{product.name} wurde in den Warenkorb gelegt.")
    return redirect("product_list")

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