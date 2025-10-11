#!/bin/sh
set -e

# Wait for database to be ready (using Python, no nc needed)
echo "Waiting for database..."
python << END
import socket
import time
import os
import sys

host = os.environ.get('DB_HOST', 'localhost')
port = int(os.environ.get('DB_PORT', 5432))

max_attempts = 30
attempt = 0

while attempt < max_attempts:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        sock.connect((host, port))
        sock.close()
        print(f"Successfully connected to {host}:{port}")
        break
    except (socket.error, socket.timeout):
        attempt += 1
        if attempt >= max_attempts:
            print(f"Failed to connect to database at {host}:{port} after {max_attempts} attempts")
            sys.exit(1)
        time.sleep(1)
END
echo "Database is ready!"

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist (optional)
if [ "${CREATE_SUPERUSER}" = "true" ]; then
    echo "Creating superuser if needed..."
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"
fi

# Start server
echo "Starting server..."
exec "$@"