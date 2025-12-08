from django.shortcuts import render
from .models import Product

def product_detail(request, product_id):
    product = Product.objects.get(id=product_id)
    return render(request, "product_detail.html", {"product": product})
