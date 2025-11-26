from django.urls import path
from . import views

urlpatterns = [
    path('api/products/', views.products_with_categories, name='products'),
    path('api/customer/<int:customer_id>/orders/', views.customer_orders, name='customer_orders'),
    path('api/order/<int:order_id>/', views.order_details, name='order_details'),
    path('api/customer/<int:customer_id>/cart/', views.cart_contents, name='cart_contents'),
    path('api/bestsellers/', views.bestselling_products, name='bestsellers'),
    path('api/low-stock/', views.low_stock_products, name='low_stock'),
    path('api/customer-stats/', views.customer_stats, name='customer_stats'),
    path('api/category-stats/', views.categories_stats, name='category_stats'),
]
