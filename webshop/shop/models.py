from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import MinValueValidator
from decimal import Decimal


class Customer(models.Model):
    """Customer model representing registered users"""
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    strasse = models.CharField(max_length=255, blank=True, null=True)
    ort = models.CharField(max_length=100, blank=True, null=True)
    plz = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        db_table = 'customer'
        indexes = [
            models.Index(fields=['email'], name='idx_customer_email'),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


class Category(models.Model):
    """Product category model"""
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.category_name


class Product(models.Model):
    """Product model representing items for sale"""
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    stock = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.RESTRICT,
        related_name='products',
        db_column='category_id'
    )

    class Meta:
        db_table = 'product'
        indexes = [
            models.Index(fields=['category'], name='idx_product_category'),
        ]

    def __str__(self):
        return f"{self.name} - €{self.price}"


class Order(models.Model):
    """Order model representing customer purchases"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    order_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='orders',
        db_column='customer_id'
    )
    order_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    class Meta:
        db_table = 'order'
        indexes = [
            models.Index(fields=['customer'], name='idx_order_customer'),
        ]

    def __str__(self):
        return f"Order {self.order_id} - {self.customer.email} - €{self.total_amount}"


class OrderItem(models.Model):
    """Order item model representing products in an order"""
    order_item_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        db_column='order_id'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.RESTRICT,
        related_name='order_items',
        db_column='product_id'
    )
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    price_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    class Meta:
        db_table = 'order_item'
        indexes = [
            models.Index(fields=['order'], name='idx_order_item_order'),
            models.Index(fields=['product'], name='idx_order_item_product'),
        ]

    def __str__(self):
        return f"{self.product.name} x {self.quantity} @ €{self.price_per_unit}"

    @property
    def subtotal(self):
        """Calculate the subtotal for this order item"""
        return self.quantity * self.price_per_unit


class Cart(models.Model):
    """Shopping cart model"""
    cart_id = models.AutoField(primary_key=True)
    customer = models.OneToOneField(
        Customer,
        on_delete=models.CASCADE,
        related_name='cart',
        db_column='customer_id'
    )
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cart'
        indexes = [
            models.Index(fields=['customer'], name='idx_cart_customer'),
        ]

    def __str__(self):
        return f"Cart for {self.customer.email}"


class CartItem(models.Model):
    """Cart item model representing products in a shopping cart"""
    cart_item_id = models.AutoField(primary_key=True)
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        db_column='cart_id'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items',
        db_column='product_id'
    )
    quantity = models.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        db_table = 'cart_item'
        unique_together = [['cart', 'product']]
        indexes = [
            models.Index(fields=['cart'], name='idx_cart_item_cart'),
            models.Index(fields=['product'], name='idx_cart_item_product'),
        ]

    def __str__(self):
        return f"{self.product.name} x {self.quantity} in cart"

    @property
    def subtotal(self):
        """Calculate the subtotal for this cart item"""
        return self.quantity * self.product.price
