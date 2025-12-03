from django.shortcuts import render
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("add_to_cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.cart_view, name="cart"),
]
