from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Product, Customer, Cart, CartItem, Category

def home(request):
    return render(request, "home.html")

def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    
    # Filter nach Kategorie
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Filter nach Preis
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Suche nach Name oder Beschreibung
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Sortierung
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    
    context = {
        "products": products,
        "categories": categories,
        "selected_category": category_id,
        "min_price": min_price,
        "max_price": max_price,
        "search_query": search_query,
        "sort_by": sort_by,
    }
    return render(request, "products.html", context)

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
            request.session["customer_name"] = customer.first_name
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