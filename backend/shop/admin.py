from django.contrib import admin
from .models import Customer, Category, Product, Order, OrderItem, Cart, CartItem


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_id', 'email', 'first_name', 'last_name', 'ort', 'plz')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('ort',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_id', 'category_name')
    search_fields = ('category_name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'name', 'price', 'stock', 'category')
    list_filter = ('category',)
    search_fields = ('name', 'description')
    list_editable = ('price', 'stock')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'customer', 'order_date', 'status', 'total_amount')
    list_filter = ('status', 'order_date')
    search_fields = ('customer__email', 'customer__first_name', 'customer__last_name')
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order_item_id', 'order', 'product', 'quantity', 'price_per_unit', 'subtotal')
    list_filter = ('order__order_date',)
    search_fields = ('product__name', 'order__customer__email')


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id', 'customer', 'last_updated', 'total')
    search_fields = ('customer__email',)
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart_item_id', 'cart', 'product', 'quantity', 'subtotal')
    search_fields = ('product__name', 'cart__customer__email')
