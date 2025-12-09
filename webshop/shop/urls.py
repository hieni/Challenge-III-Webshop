from django.shortcuts import render
from django.urls import path
from . import views, views_cart, views_login, views_order, views_product, views_wishlist

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path("login/", views_login.login_view, name="login"),
    path("logout/", views_login.logout_view, name="logout"),
    path("add_to_cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views_cart.cart_view, name="cart"),
    path("cart/increase/<int:item_id>/", views_cart.cart_increase, name="cart_increase"),
    path("cart/decrease/<int:item_id>/", views_cart.cart_decrease, name="cart_decrease"),
    path("cart/remove/<int:item_id>/", views_cart.cart_remove, name="cart_remove"),
    path("checkout_page/", views_cart.checkout_page, name="checkout_page"),
    path("orders/", views_order.orders_list, name="orders_list"),
    path("orders/<int:order_id>/", views_order.order_detail, name="order_detail"),
    path("product/<int:product_id>/", views_product.product_detail, name="product_detail"),
    path("wishlist/", views_wishlist.wishlist_view, name="wishlist"),
    path("wishlist/add/<int:product_id>/", views_wishlist.wishlist_add, name="wishlist_add"),
    path("register/", views_login.register_view, name="register"),
    path("checkout/", views_cart.checkout, name="checkout"),

]
