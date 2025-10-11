#!/bin/sh
set -e

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
fi

# Wait for database to be ready (using Python, no nc needed)
echo "Waiting for database..."
python << 'END'
import socket
import time
import os
import sys

host = os.environ.get('DB_HOST', 'localhost')
port = int(os.environ.get('DB_PORT', 5432))

print(f"Attempting to connect to database at {host}:{port}...")

max_attempts = 30
attempt = 0

while attempt < max_attempts:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            print(f"Successfully connected to {host}:{port}")
            sys.exit(0)
        else:
            raise ConnectionError(f"Connection failed with code: {result}")
    except Exception as e:
        attempt += 1
        if attempt >= max_attempts:
            print(f"Failed to connect to database at {host}:{port} after {max_attempts} attempts")
            print(f"Last error: {str(e)}")
            sys.exit(1)
        print(f"Attempt {attempt}/{max_attempts} failed, retrying in 2 seconds...")
        time.sleep(2)
END

echo "Database is ready!"

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Seed database (optional)
if [ "${SEED_DATABASE}" = "true" ]; then
    echo "Seeding database from CSV files..."
    python manage.py seed_data
fi

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