#!/bin/bash
set -e

echo "==> Waiting for PostgreSQL..."
until PGPASSWORD=$DATABASE_PASSWORD psql -h "$DATABASE_HOST" -U "$DATABASE_USERNAME" -d "$DATABASE_NAME" -c '\q' 2>/dev/null; do
  sleep 1
done
echo "==> PostgreSQL is ready!"

echo "==> Running migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "==> Loading fixtures..."
python manage.py loaddata shop/fixtures/data.yaml 2>/dev/null || echo "Fixtures already loaded or not found"

echo "==> Creating superuser..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
EOF

echo "==> Starting Django development server..."
exec python manage.py runserver 0.0.0.0:8000
