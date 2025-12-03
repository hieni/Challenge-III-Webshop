from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Product, Customer

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