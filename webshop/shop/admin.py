from django.contrib import admin
from .models import Customer, Category, Product, Order, OrderItem, Cart, CartItem

admin.site.register([Customer, Category, Product, Order, OrderItem, Cart, CartItem])
