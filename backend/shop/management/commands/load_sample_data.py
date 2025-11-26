from django.core.management.base import BaseCommand
from shop.models import Customer, Category, Product, Order, OrderItem, Cart, CartItem
from decimal import Decimal
from datetime import date


class Command(BaseCommand):
    help = 'Load sample data into the database'

    def handle(self, *args, **kwargs):
        self.stdout.write('Loading sample data...')

        # Create Categories
        categories_data = [
            'Electronics', 'Home', 'Industrial', 'Sports', 'Music',
            'Jewelry', 'Games', 'Grocery', 'Toys', 'Movies',
            'Automotive', 'Health', 'Garden', 'Clothing', 'Beauty',
            'Computers', 'Shoes', 'Kids', 'Books', 'Outdoors', 'Baby', 'Tools'
        ]
        
        categories = {}
        for cat_name in categories_data:
            cat, created = Category.objects.get_or_create(category_name=cat_name)
            categories[cat_name] = cat
            if created:
                self.stdout.write(f'  Created category: {cat_name}')

        # Create Sample Customers
        customers_data = [
            {
                'first_name': 'Deborah', 'last_name': 'Bruen',
                'email': 'deborah.bruen@example.com', 'password': 'hashed_password_1',
                'strasse': '39763 Glenda Harbors', 'ort': 'Whittier', 'plz': '69550-9013'
            },
            {
                'first_name': 'Guadalupe', 'last_name': 'Gorczany',
                'email': 'guadalupe.gorczany@example.com', 'password': 'hashed_password_2',
                'strasse': '9819 Leilani Points', 'ort': 'Fort Wavahaven', 'plz': '11692'
            },
            {
                'first_name': 'Betty', 'last_name': 'Watsica',
                'email': 'betty.watsica@example.com', 'password': 'hashed_password_3',
                'strasse': '384 Union Avenue', 'ort': 'North Janfield', 'plz': '02372-1383'
            },
            {
                'first_name': 'Sidney', 'last_name': 'Tromp',
                'email': 'sidney.tromp@example.com', 'password': 'hashed_password_4',
                'strasse': '47396 The Woodlands', 'ort': 'Ritchieboro', 'plz': '31756-8559'
            },
            {
                'first_name': 'Miranda', 'last_name': 'Marvin',
                'email': 'miranda.marvin@example.com', 'password': 'hashed_password_5',
                'strasse': '81781 Mann Port', 'ort': 'South Jaquanberg', 'plz': '00345-1100'
            },
        ]

        customers = []
        for cust_data in customers_data:
            cust, created = Customer.objects.get_or_create(
                email=cust_data['email'],
                defaults=cust_data
            )
            customers.append(cust)
            if created:
                self.stdout.write(f'  Created customer: {cust.email}')

        # Create Sample Products
        products_data = [
            {'name': 'Elegant Marble Gloves', 'description': 'High quality marble gloves', 
             'price': Decimal('235.99'), 'stock': 58, 'category': 'Home'},
            {'name': 'Intelligent Gold Hat', 'description': 'Premium gold hat',
             'price': Decimal('975.29'), 'stock': 51, 'category': 'Industrial'},
            {'name': 'Handmade Wooden Computer', 'description': 'Artisan wooden computer',
             'price': Decimal('369.35'), 'stock': 2, 'category': 'Electronics'},
            {'name': 'Refined Silk Sausages', 'description': 'Luxury silk sausages',
             'price': Decimal('882.59'), 'stock': 85, 'category': 'Sports'},
            {'name': 'Bespoke Plastic Bacon', 'description': 'Custom plastic bacon',
             'price': Decimal('262.39'), 'stock': 44, 'category': 'Music'},
            {'name': 'Oriental Rubber Gloves', 'description': 'Exotic rubber gloves',
             'price': Decimal('970.59'), 'stock': 16, 'category': 'Jewelry'},
            {'name': 'Modern Aluminum Pizza', 'description': 'Contemporary aluminum pizza',
             'price': Decimal('916.19'), 'stock': 68, 'category': 'Home'},
            {'name': 'Unbranded Steel Mouse', 'description': 'Generic steel mouse',
             'price': Decimal('485.78'), 'stock': 31, 'category': 'Games'},
            {'name': 'Awesome Aluminum Cheese', 'description': 'Amazing aluminum cheese',
             'price': Decimal('996.23'), 'stock': 33, 'category': 'Grocery'},
            {'name': 'Oriental Concrete Tuna', 'description': 'Exotic concrete tuna',
             'price': Decimal('886.85'), 'stock': 84, 'category': 'Toys'},
        ]

        products = []
        for prod_data in products_data:
            cat_name = prod_data.pop('category')
            prod, created = Product.objects.get_or_create(
                name=prod_data['name'],
                defaults={**prod_data, 'category': categories[cat_name]}
            )
            products.append(prod)
            if created:
                self.stdout.write(f'  Created product: {prod.name}')

        # Create Sample Orders
        if customers and products:
            order, created = Order.objects.get_or_create(
                customer=customers[0],
                defaults={
                    'status': 'completed',
                    'total_amount': Decimal('910.65')
                }
            )
            if created:
                self.stdout.write(f'  Created order: {order}')
                OrderItem.objects.create(
                    order=order,
                    product=products[0],
                    quantity=2,
                    price_per_unit=products[0].price
                )

            # Create Cart for first customer
            cart, created = Cart.objects.get_or_create(customer=customers[0])
            if created:
                self.stdout.write(f'  Created cart for: {customers[0].email}')
                CartItem.objects.create(cart=cart, product=products[1], quantity=1)
                CartItem.objects.create(cart=cart, product=products[2], quantity=3)

        self.stdout.write(self.style.SUCCESS('Successfully loaded sample data!'))
