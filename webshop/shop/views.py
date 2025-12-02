from django.shortcuts import render
from .models import Product

def home(request):
    return render(request, "home.html")

def product_list(request):
    products = Product.objects.all()
    return render(request, "products.html", {"products": products})