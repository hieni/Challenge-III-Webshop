from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Customer
from django.db import IntegrityError

def register_view(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        street = request.POST.get("street")
        city = request.POST.get("city")
        postal_code = request.POST.get("postal_code")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Die Passwörter stimmen nicht überein.")
            return redirect("register")

        if Customer.objects.filter(email=email).exists():
            messages.error(request, "Diese E-Mail wird bereits verwendet.")
            return redirect("register")

        customer = Customer(
            first_name=first_name,
            last_name=last_name,
            email=email,
            street=street,
            city=city,
            postal_code=postal_code,
        )
        customer.set_password(password1)
        customer.save()

        request.session["customer_id"] = customer.id

        messages.success(request, f"Willkommen, {customer.first_name}! Dein Account wurde erstellt.")
        return redirect("product_list")

    return render(request, "register.html")

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