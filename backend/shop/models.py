from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Customer(models.Model):
    """Customer model representing webshop customers"""
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
        
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


class Category(models.Model):
    """Product category model"""
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'category'
        verbose_name_plural = 'Categories'
        
    def __str__(self):
        return self.category_name


class Product(models.Model):
    """Product model with relationship to Category"""
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
        db_column='category_id',
        related_name='products'
    )

    class Meta:
        db_table = 'product'
        indexes = [
            models.Index(fields=['category']),
        ]
        
    def __str__(self):
        return f"{self.name} - ${self.price}"


class Order(models.Model):
    """Order model representing customer orders"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    order_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        db_column='customer_id',
        related_name='orders'
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
            models.Index(fields=['customer']),
            models.Index(fields=['order_date']),
        ]
        
    def __str__(self):
        return f"Order #{self.order_id} - {self.customer.email} - ${self.total_amount}"


class OrderItem(models.Model):
    """Order item model - junction table between Order and Product"""
    order_item_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        db_column='order_id',
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.RESTRICT,
        db_column='product_id',
        related_name='order_items'
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
            models.Index(fields=['order']),
            models.Index(fields=['product']),
        ]
        
    def __str__(self):
        return f"{self.product.name} x{self.quantity} in Order #{self.order.order_id}"
    
    @property
    def subtotal(self):
        return self.quantity * self.price_per_unit


class Cart(models.Model):
    """Shopping cart model - one per customer"""
    cart_id = models.AutoField(primary_key=True)
    customer = models.OneToOneField(
        Customer,
        on_delete=models.CASCADE,
        db_column='customer_id',
        related_name='cart'
    )
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cart'
        indexes = [
            models.Index(fields=['customer']),
        ]
        
    def __str__(self):
        return f"Cart for {self.customer.email}"
    
    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())


class CartItem(models.Model):
    """Cart item model - junction table between Cart and Product"""
    cart_item_id = models.AutoField(primary_key=True)
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        db_column='cart_id',
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        db_column='product_id',
        related_name='cart_items'
    )
    quantity = models.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        db_table = 'cart_item'
        unique_together = [['cart', 'product']]
        indexes = [
            models.Index(fields=['cart']),
            models.Index(fields=['product']),
        ]
        
    def __str__(self):
        return f"{self.product.name} x{self.quantity} in {self.cart.customer.email}'s cart"
    
    @property
    def subtotal(self):
        return self.quantity * self.product.price
