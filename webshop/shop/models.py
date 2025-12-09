from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class Customer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=128)
    default_billing_address = models.ForeignKey(
        "Address",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="billing_customers",
    )
    default_shipping_address = models.ForeignKey(
        "Address",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="shipping_customers",
    )

    def set_password(self, raw_password):
        self.password_hash = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password_hash)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Category(models.Model):
    category_name = models.CharField(max_length=50)

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="products/", null=True, blank=True)

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="orders")
    billing_address = models.ForeignKey(
        "Address",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="billing_orders",
    )
    shipment_address = models.ForeignKey(
        "Address",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="shipment_orders",
    )
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)
    
    def get_total_amount(self):
        return sum(item.price_per_unit * item.quantity for item in self.orderitem_set.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)

class Cart(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name="cart")
    last_updated = models.DateTimeField(auto_now=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

class Wishlist(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name="wishlist")
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


class Address(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="addresses")
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=20)

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
    ("paypal", "PayPal"),
    ("invoice", "Invoice"), 
    ]
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=32, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=50)


class Shipment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="shipments")
    shipped_date = models.DateTimeField(null=True, blank=True)
    delivery_date = models.DateTimeField(null=True, blank=True)
    carrier = models.CharField(max_length=100, blank=True)
    tracking_number = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=50, blank=True)