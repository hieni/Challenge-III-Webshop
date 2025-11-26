#!/bin/bash

echo "Starting Django application..."

# Wait for database to be ready
echo "Waiting for database..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "Database is ready!"

# Run migrations
echo "Running database migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Create superuser if it doesn't exist
echo "Creating superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123');
    print('Superuser created: admin/admin123');
else:
    print('Superuser already exists');
"

# Load sample data if database is empty
echo "Loading sample data..."
python manage.py shell -c "
from shop.models import Product;
if Product.objects.count() == 0:
    import subprocess;
    subprocess.run(['python', 'manage.py', 'load_sample_data']);
    print('Sample data loaded');
else:
    print('Sample data already exists');
"

echo "Starting server..."
exec "$@"
