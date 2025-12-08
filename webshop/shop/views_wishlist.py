from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Wishlist, WishlistItem, Customer

def wishlist_view(request):
    customer = Customer.objects.get(id=request.session["customer_id"])
    wishlist, _ = Wishlist.objects.get_or_create(customer=customer)
    items = WishlistItem.objects.filter(wishlist=wishlist)
    return render(request, "wishlist.html", {"items": items})

def wishlist_add(request, product_id):
    customer_id = request.session.get("customer_id")
    if not customer_id:
        messages.error(request, "Bitte logge dich ein, um Artikel zum Warenkorb hinzuzufügen.")
        return redirect("product_list")

    customer = Customer.objects.get(id=customer_id)
    
    wishlist, _ = Wishlist.objects.get_or_create(customer=customer)

    WishlistItem.objects.get_or_create(
        wishlist=wishlist,
        product_id=product_id
    )

    messages.success(request, "Zur Wunschliste hinzugefügt.")
    return redirect("product_detail", product_id=product_id)
