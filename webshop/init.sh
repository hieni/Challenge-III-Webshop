#!/bin/bash

echo "Starting Django application..."

# Wait for database to be ready
echo "Waiting for database..."
while ! (echo > /dev/tcp/db/5432) >/dev/null 2>&1; do
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
    User.objects.create_superuser('admin', 'admin@example.com', '1234');
    print('Superuser created: admin/1234');
else:
    print('Superuser already exists');
"

# Load sample data if database is empty
echo "Loading sample data..."
python manage.py loaddata data.yaml

echo "Starting server..."
exec "$@"