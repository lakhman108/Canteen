# Docker Setup for Django Canteen Application

## Quick Start

### Development
```bash
# Build and run with development settings
docker-compose up --build

# Run in background
docker-compose up -d --build

# View logs
docker-compose logs -f web
```

### Production
```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up --build -d
```

## What's Included

### Services
- **web**: Django application running on port 8000
- **db**: PostgreSQL 15 database

### Features
- Automatic database migrations
- Static file collection
- Health checks for database
- Auto-creation of admin superuser (admin/admin123)
- Optimized Docker image with minimal dependencies

## Environment Variables

For production, create a `.env` file with:
```
SECRET_KEY=your-secret-key-here
DEBUG=False
DB_NAME=canteen_db
DB_USER=postgres
DB_PASSWORD=your-secure-password
ALLOWED_HOSTS=yourdomain.com,localhost
RAZORPAY_KEY_ID=your-razorpay-key
RAZORPAY_KEY_SECRET=your-razorpay-secret
```

## Useful Commands

```bash
# Stop services
docker-compose down

# Remove volumes (careful - deletes database data)
docker-compose down -v

# Rebuild only web service
docker-compose build web

# Run Django commands
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py shell

# View database
docker-compose exec db psql -U postgres -d canteen_db
```

## File Changes Made

1. **requirements-minimal.txt**: Reduced from 50+ to 10 essential packages
2. **Dockerfile.optimized**: Multi-stage build with security best practices
3. **docker-compose.yml**: Development setup with auto-reload
4. **docker-compose.prod.yml**: Production-ready configuration
5. **.dockerignore**: Excludes unnecessary files from build context
6. **docker-entrypoint.sh**: Handles migrations and setup automatically

## Access Points

- Application: http://localhost:8000
- Admin Panel: http://localhost:8000/admin (admin/admin123)
- Database: localhost:5432