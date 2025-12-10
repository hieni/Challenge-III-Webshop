from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.core.validators import MinValueValidator
from decimal import Decimal


class Customer(models.Model):
    """Customer model with authentication and address management."""
    first_name = models.CharField(max_length=50, verbose_name="Vorname")
    last_name = models.CharField(max_length=50, verbose_name="Nachname")
    email = models.EmailField(unique=True, verbose_name="E-Mail")
    password_hash = models.CharField(max_length=128)
    default_billing_address = models.ForeignKey(
        "Address",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="billing_customers",
        verbose_name="Standard Rechnungsadresse"
    )
    default_shipping_address = models.ForeignKey(
        "Address",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="shipping_customers",
        verbose_name="Standard Versandadresse"
    )
    
    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = "Kunde"
        verbose_name_plural = "Kunden"
    
    def set_password(self, raw_password):
        """Hash and set password."""
        self.password_hash = make_password(raw_password)

    def check_password(self, raw_password):
        """Verify password against hash."""
        return check_password(raw_password, self.password_hash)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


class Address(models.Model):
    """Customer address for billing and shipping."""
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="addresses",
        verbose_name="Kunde"
    )
    street = models.CharField(max_length=100, verbose_name="Straße")
    city = models.CharField(max_length=50, verbose_name="Stadt")
    postal_code = models.CharField(max_length=20, verbose_name="Postleitzahl")
    country = models.CharField(max_length=50, default="Germany", verbose_name="Land")
    
    class Meta:
        verbose_name = "Adresse"
        verbose_name_plural = "Adressen"
    
    def __str__(self):
        return f"{self.street}, {self.postal_code} {self.city}, {self.country}"


class Category(models.Model):
    """Product category."""
    category_name = models.CharField(max_length=50, unique=True, verbose_name="Kategorie")
    
    class Meta:
        ordering = ['category_name']
        verbose_name = "Kategorie"
        verbose_name_plural = "Kategorien"
    
    def __str__(self):
        return self.category_name


class Product(models.Model):
    """Product with stock management."""
    name = models.CharField(max_length=100, verbose_name="Produktname")
    description = models.TextField(verbose_name="Beschreibung")
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Preis"
    )
    stock = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Lagerbestand"
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Kategorie"
    )
    image = models.ImageField(
        upload_to="products/", 
        null=True, 
        blank=True,
        verbose_name="Produktbild"
    )
    
    class Meta:
        ordering = ['name']
        verbose_name = "Produkt"
        verbose_name_plural = "Produkte"
    
    def __str__(self):
        return f"{self.name} (€{self.price})"
    
    def is_in_stock(self):
        """Check if product is available."""
        return self.stock > 0
    
    def is_low_stock(self):
        """Check if stock is low (≤5)."""
        return 0 < self.stock <= 5


class Order(models.Model):
    """Customer order with status tracking and address management."""
    STATUS_CHOICES = [
        ('pending', 'Ausstehend'),
        ('processing', 'In Bearbeitung'),
        ('shipped', 'Versendet'),
        ('delivered', 'Zugestellt'),
        ('cancelled', 'Storniert'),
    ]
    
    customer = models.ForeignKey(
        Customer, 
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Kunde"
    )
    billing_address = models.ForeignKey(
        Address,
        on_delete=models.PROTECT,
        related_name="billing_orders",
        verbose_name="Rechnungsadresse",
        help_text="Pflichtfeld: Rechnungsadresse muss angegeben werden"
    )
    shipment_address = models.ForeignKey(
        Address,
        on_delete=models.PROTECT,
        related_name="shipment_orders",
        verbose_name="Versandadresse",
        help_text="Pflichtfeld: Lieferadresse muss angegeben werden"
    )
    order_date = models.DateTimeField(auto_now_add=True, verbose_name="Bestelldatum")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Status"
    )
    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Gesamtbetrag"
    )
    
    class Meta:
        ordering = ['-order_date']
        verbose_name = "Bestellung"
        verbose_name_plural = "Bestellungen"
    
    def __str__(self):
        return f"Bestellung #{self.id} - {self.customer} (€{self.total_amount})"


class OrderItem(models.Model):
    """Individual item in an order."""
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Bestellung"
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        verbose_name="Produkt"
    )
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Menge"
    )
    price_per_unit = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Einzelpreis"
    )
    
    class Meta:
        verbose_name = "Bestellposition"
        verbose_name_plural = "Bestellpositionen"
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name} (Bestellung #{self.order.id})"
    
    def get_subtotal(self):
        """Calculate subtotal for this item."""
        return self.quantity * self.price_per_unit


class Cart(models.Model):
    """Shopping cart for customer."""
    customer = models.OneToOneField(
        Customer, 
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name="Kunde"
    )
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Zuletzt aktualisiert")
    
    class Meta:
        verbose_name = "Warenkorb"
        verbose_name_plural = "Warenkörbe"
    
    def __str__(self):
        return f"Warenkorb von {self.customer}"
    
    def get_total(self):
        """Calculate total cart value."""
        return sum(item.get_subtotal() for item in self.items.all())


class CartItem(models.Model):
    """Item in shopping cart."""
    cart = models.ForeignKey(
        Cart, 
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Warenkorb"
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        verbose_name="Produkt"
    )
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Menge"
    )
    
    class Meta:
        unique_together = ['cart', 'product']
        verbose_name = "Warenkorb-Position"
        verbose_name_plural = "Warenkorb-Positionen"
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
    
    def get_subtotal(self):
        """Calculate subtotal for this cart item."""
        return self.quantity * self.product.price


class Wishlist(models.Model):
    """Customer wishlist."""
    customer = models.OneToOneField(
        Customer, 
        on_delete=models.CASCADE,
        related_name="wishlist",
        verbose_name="Kunde"
    )
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Zuletzt aktualisiert")
    
    class Meta:
        verbose_name = "Wunschliste"
        verbose_name_plural = "Wunschlisten"
    
    def __str__(self):
        return f"Wunschliste von {self.customer}"


class WishlistItem(models.Model):
    """Item in wishlist."""
    wishlist = models.ForeignKey(
        Wishlist, 
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Wunschliste"
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        verbose_name="Produkt"
    )
    
    class Meta:
        unique_together = ['wishlist', 'product']
        verbose_name = "Wunschlisten-Position"
        verbose_name_plural = "Wunschlisten-Positionen"
    
    def __str__(self):
        return f"{self.product.name} (Wunschliste von {self.wishlist.customer})"


class Payment(models.Model):
    """Payment tracking for orders."""
    PAYMENT_METHOD_CHOICES = [
        ("paypal", "PayPal"),
        ("credit_card", "Kreditkarte"),
        ("invoice", "Rechnung"),
        ("bank_transfer", "Überweisung"),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ("pending", "Ausstehend"),
        ("completed", "Abgeschlossen"),
        ("failed", "Fehlgeschlagen"),
        ("refunded", "Erstattet"),
    ]
    
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="payment",
        verbose_name="Bestellung"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Betrag"
    )
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name="Zahlungsdatum")
    payment_method = models.CharField(
        max_length=32,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name="Zahlungsmethode"
    )
    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="pending",
        verbose_name="Status"
    )
    transaction_id = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Transaktions-ID"
    )
    
    class Meta:
        verbose_name = "Zahlung"
        verbose_name_plural = "Zahlungen"
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"Zahlung #{self.id} - Bestellung #{self.order.id} (€{self.amount}) - {self.get_status_display()}"


class Shipment(models.Model):
    """Shipment tracking for orders."""
    SHIPMENT_STATUS_CHOICES = [
        ("pending", "Ausstehend"),
        ("preparing", "Wird vorbereitet"),
        ("shipped", "Versendet"),
        ("in_transit", "Unterwegs"),
        ("delivered", "Zugestellt"),
        ("returned", "Zurückgesendet"),
    ]
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="shipments",
        verbose_name="Bestellung"
    )
    shipped_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Versanddatum"
    )
    delivery_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Zustelldatum"
    )
    carrier = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Versanddienstleister"
    )
    tracking_number = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Tracking-Nummer"
    )
    status = models.CharField(
        max_length=20,
        choices=SHIPMENT_STATUS_CHOICES,
        default="pending",
        verbose_name="Status"
    )
    
    class Meta:
        verbose_name = "Versand"
        verbose_name_plural = "Versendungen"
        ordering = ['-shipped_date']
    
    def __str__(self):
        return f"Versand #{self.id} - Bestellung #{self.order.id} - {self.get_status_display()}"
    
    def get_tracking_url(self):
        """Generate tracking URL based on carrier."""
        if not self.tracking_number:
            return None
        
        carrier_urls = {
            "DHL": f"https://www.dhl.de/de/privatkunden/pakete-empfangen/verfolgen.html?piececode={self.tracking_number}",
            "DPD": f"https://tracking.dpd.de/status/de_DE/parcel/{self.tracking_number}",
            "UPS": f"https://www.ups.com/track?tracknum={self.tracking_number}",
            "Hermes": f"https://www.myhermes.de/empfangen/sendungsverfolgung/sendungsinformation/#/{self.tracking_number}",
        }
        
        return carrier_urls.get(self.carrier, None)
