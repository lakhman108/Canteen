# 🍽️ Canteen Management System

A comprehensive Django-based canteen management web application with integrated payment processing, real-time order tracking, and administrative controls.

[![Django](https://img.shields.io/badge/Django-4.1.13-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
  - [Local Development](#local-development)
  - [Docker Deployment](#docker-deployment)
- [Configuration](#-configuration)
- [Database Seeding](#-database-seeding)
- [API Documentation](#-api-documentation)
- [Usage](#-usage)
- [Admin Panel](#-admin-panel)
- [Payment Integration](#-payment-integration)
- [Contributing](#-contributing)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)

## ✨ Features

### 🛒 Customer Features
- **User Authentication**: Secure registration and login system
- **Browse Menu**: View food items with categories, images, prices, and ratings
- **Filter by Category**: Browse items by cuisine type (Gujarati, Punjabi, Chinese, South Indian, Snacks)
- **Shopping Cart**: Add/remove items, adjust quantities, real-time stock validation
- **Payment Processing**: Integrated Razorpay payment gateway
- **Order Tracking**: Real-time order status updates
- **Responsive Design**: Mobile-friendly interface

### 👨‍💼 Admin Features
- **Order Management**: View pending orders, mark items as delivered
- **Inventory Management**: Add/update food items and categories
- **Real-time Dashboard**: Monitor active orders and delivery status
- **Stock Management**: Track and update stock quantities
- **User Management**: View and manage customer accounts

### 🔧 Technical Features
- **RESTful API**: Complete API for all operations
- **Database Optimization**: Query optimization with select_related and prefetch_related
- **Docker Support**: Containerized deployment with Docker Compose
- **Database Seeding**: CSV-based data import for easy setup
- **Payment Verification**: Razorpay signature verification
- **Session Management**: Secure user sessions
- **Error Handling**: Comprehensive error handling and user feedback

## 🛠️ Tech Stack

### Backend
- **Framework**: Django 4.1.13
- **API**: Django REST Framework 3.15.1
- **Database**: PostgreSQL 15
- **ORM**: Django ORM
- **Server**: Gunicorn 22.0.0

### Frontend
- **Template Engine**: Django Templates
- **Styling**: CSS, Bootstrap (via templates)
- **JavaScript**: Vanilla JS for dynamic interactions

### Payment & Integration
- **Payment Gateway**: Razorpay 1.4.2
- **HTTP Client**: Requests 2.32.0

### DevOps & Deployment
- **Containerization**: Docker & Docker Compose
- **Static Files**: WhiteNoise 6.6.0
- **Environment Management**: python-dotenv 1.0.1

## 📁 Project Structure

```
Canteen/
├── canteen/                    # Main application
│   ├── management/            # Custom management commands
│   │   └── commands/
│   │       └── seed_data.py   # Database seeding command
│   ├── migrations/            # Database migrations
│   ├── models.py              # Data models (CustomUser, Orders, Food, etc.)
│   ├── views.py               # View functions
│   ├── urls.py                # URL routing
│   ├── forms.py               # Form definitions
│   └── admin.py               # Admin configurations
├── admin_panel/               # Admin interface
│   ├── views.py               # Admin-specific views
│   └── urls.py                # Admin URL routing
├── database/                  # API application
│   ├── models.py              # Additional models
│   ├── views.py               # API ViewSets
│   ├── serializers.py         # DRF serializers
│   └── urls.py                # API routing
├── vercel_app/                # Project configuration
│   ├── settings.py            # Django settings
│   ├── urls.py                # Main URL configuration
│   └── wsgi.py                # WSGI configuration
├── templates/                 # HTML templates
│   ├── base.html
│   ├── index.html             # Menu page
│   ├── cart.html              # Shopping cart
│   ├── payment.html           # Payment page
│   ├── OrderStatus.html       # Order status
│   └── admin/                 # Admin templates
├── static/                    # Static files (CSS, JS, images)
├── canteen_food.csv           # Food categories seed data
├── canteen_fooddetails.csv    # Food items seed data
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Docker Compose configuration
├── docker-entrypoint.sh       # Container startup script
├── requirements.txt           # Python dependencies
├── manage.py                  # Django management script
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## 📦 Prerequisites

### Local Development
- Python 3.9 or higher
- PostgreSQL 15 or higher
- pip (Python package manager)

### Docker Deployment
- Docker 20.10+
- Docker Compose 2.0+

## 🚀 Installation

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/lakhman108/Canteen.git
   cd Canteen
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Configure PostgreSQL**
   ```bash
   # Create database
   createdb canteen_db
   
   # Or using psql
   psql -U postgres
   CREATE DATABASE canteen_db;
   ```

6. **Run migrations**
   ```bash
   python manage.py migrate
   ```

7. **Seed the database (optional)**
   ```bash
   python manage.py seed_data
   ```

8. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

9. **Collect static files**
   ```bash
   python manage.py collectstatic --noinput
   ```

10. **Run the development server**
    ```bash
    python manage.py runserver
    ```

11. **Access the application**
    - Main site: http://localhost:8000
    - Admin panel: http://localhost:8000/admin
    - API: http://localhost:8000/api

### Docker Deployment

1. **Clone the repository**
   ```bash
   git clone https://github.com/lakhman108/Canteen.git
   cd Canteen
   ```

2. **Create and configure .env file**
   ```bash
   cp .env.example .env
   # Edit .env with your external database credentials
   ```

3. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Main site: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

5. **Stop the containers**
   ```bash
   docker-compose down
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here-change-this-in-production
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Database Configuration (External PostgreSQL)
DB_NAME=canteen_db
DB_USER=postgres
DB_PASSWORD=your-database-password
DB_HOST=your-database-host.com
DB_PORT=5432
DB_SSLMODE=require

# Application Settings
BASE_URL=http://localhost:8000

# Optional: Auto-create superuser on startup
CREATE_SUPERUSER=false

# Optional: Auto-seed database on startup
SEED_DATABASE=false

# Payment Gateway (Razorpay)
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-secret-key
```

### Database Configuration

The application supports PostgreSQL as the primary database. Update your `.env` file with your database credentials:

- **Local PostgreSQL**: Use `DB_HOST=localhost`
- **Docker PostgreSQL**: Use the service name from docker-compose.yml
- **Cloud Database**: Use the provided connection details (AWS RDS, Azure Database, etc.)

## 🌱 Database Seeding

The project includes a custom management command to seed the database with food categories and items from CSV files.

### Seed Data Files

- `canteen_food.csv`: Food categories (Gujarati, Punjabi, Chinese, South Indian, Snacks)
- `canteen_fooddetails.csv`: Individual food items with details

### Seeding Methods

**Method 1: Manual Command**
```bash
# Seed the database
python manage.py seed_data

# Clear existing data and reseed
python manage.py seed_data --clear
```

**Method 2: Auto-seed with Docker**
```bash
# Set in .env file
SEED_DATABASE=true

# Then run
docker-compose up --build
```

**Method 3: Inside Docker Container**
```bash
docker-compose exec web python manage.py seed_data
```

For more details, see [SEEDING_GUIDE.md](SEEDING_GUIDE.md)

## 📡 API Documentation

The application provides a RESTful API for all major operations.

### Base URL
```
http://localhost:8000/api/
```

### API Endpoints

#### Users
- `GET /api/customusers/` - List all users
- `POST /api/customusers/` - Create a new user
- `GET /api/customusers/{id}/` - Get user details
- `GET /api/customusers/{id}/orders/` - Get user's orders

#### Food Categories
- `GET /api/food/` - List all food categories
- `POST /api/food/` - Create a food category
- `GET /api/food/{id}/` - Get category details

#### Food Items
- `GET /api/fooddetails/` - List all food items
- `POST /api/fooddetails/` - Create a food item
- `POST /api/fooddetails/additem/` - Add item with validation
- `GET /api/fooddetails/{id}/` - Get item details

#### Orders
- `GET /api/orders/` - List all orders
- `POST /api/orders/` - Create an order
- `GET /api/orders/{id}/` - Get order details
- `GET /api/orders/{id}/orderdetails/` - Get order items
- `GET /api/orders/remainingorders/` - Get pending paid orders

#### Order Details
- `GET /api/orderdetails/` - List all order details
- `POST /api/orderdetails/` - Add item to order
- `PUT /api/orderdetails/{id}/` - Update order detail
- `DELETE /api/orderdetails/{id}/` - Remove item from order

#### Payments
- `GET /api/payment/` - List all payments
- `POST /api/payment/` - Create payment
- `GET /api/payment/{id}/paymentdeatils/` - Get payment details

### Example API Request

```bash
# Get all food items
curl -X GET http://localhost:8000/api/fooddetails/

# Add item to cart
curl -X POST http://localhost:8000/api/orderdetails/ \
  -H "Content-Type: application/json" \
  -d '{
    "order": 1,
    "item": 5,
    "qty": 2
  }'
```

## 💻 Usage

### Customer Workflow

1. **Register/Login**
   - Navigate to `/canteen/register/` to create an account
   - Login at `/canteen/login/`

2. **Browse Menu**
   - View all food items on the home page
   - Filter by category using the filter options
   - Check item availability, price, and ratings

3. **Add to Cart**
   - Click "Add to Cart" on desired items
   - Items are automatically validated for stock availability
   - View cart at `/canteen/cart`

4. **Manage Cart**
   - Adjust quantities using +/- buttons
   - Remove unwanted items
   - View real-time price calculation

5. **Checkout & Payment**
   - Click "Proceed to Payment"
   - Complete payment via Razorpay
   - Receive order confirmation

6. **Track Order**
   - View order status on confirmation page
   - Wait for order preparation and delivery notification

### Admin Workflow

1. **Access Admin Panel**
   - Login with staff credentials
   - Navigate to `/admin_panel/`

2. **View Orders**
   - See all pending paid orders
   - View order details and items

3. **Process Orders**
   - Mark items as delivered
   - Update order status
   - Complete orders when all items delivered

4. **Manage Inventory**
   - Add new food items
   - Update prices and stock
   - Manage food categories

## 🔐 Admin Panel

### Access
- URL: `/admin/` (Django Admin) or `/admin_panel/` (Custom Admin)
- Requires staff/superuser credentials

### Features
- **Order Management**: View and process orders
- **User Management**: Manage customer accounts
- **Food Management**: Add/edit food items and categories
- **Payment Tracking**: Monitor payment status
- **Delivery Status**: Update order delivery status

### Creating Admin User

```bash
# Local development
python manage.py createsuperuser

# Docker
docker-compose exec web python manage.py createsuperuser
```

## 💳 Payment Integration

The application uses **Razorpay** for secure payment processing.

### Setup

1. **Get Razorpay Credentials**
   - Sign up at [Razorpay Dashboard](https://dashboard.razorpay.com/)
   - Get your API Key ID and Secret

2. **Configure Environment Variables**
   ```env
   RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxxx
   RAZORPAY_KEY_SECRET=your_secret_key_here
   ```

3. **Test Mode**
   - Use test credentials for development
   - Test card: 4111 1111 1111 1111
   - CVV: Any 3 digits
   - Expiry: Any future date

4. **Production Mode**
   - Replace test credentials with live credentials
   - Enable production mode in Razorpay dashboard
   - Set up webhooks for payment notifications

### Payment Flow

1. User proceeds to checkout from cart
2. Total amount is calculated
3. Razorpay order is created
4. Payment modal opens with order details
5. User completes payment
6. Payment signature is verified
7. Order status is updated to "Paid"
8. User sees order confirmation

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Style
- Follow PEP 8 guidelines for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Write docstrings for functions and classes

## 🐛 Troubleshooting

### Common Issues

**Database Connection Error**
```bash
# Check if PostgreSQL is running
sudo service postgresql status

# Verify database credentials in .env
# Test connection
psql -h $DB_HOST -U $DB_USER -d $DB_NAME
```

**Migration Issues**
```bash
# Reset migrations (development only)
python manage.py migrate --fake canteen zero
python manage.py migrate canteen

# Or delete migration files and recreate
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
python manage.py makemigrations
python manage.py migrate
```

**Static Files Not Loading**
```bash
# Collect static files
python manage.py collectstatic --noinput

# Check STATIC_ROOT and STATIC_URL in settings.py
```

**Payment Gateway Errors**
- Verify Razorpay credentials in .env
- Check if using correct mode (test vs live)
- Review Razorpay dashboard for error logs

**Docker Issues**
```bash
# Rebuild containers
docker-compose down -v
docker-compose up --build

# View logs
docker-compose logs -f web

# Access container shell
docker-compose exec web bash
```

### Getting Help

- Check [SEEDING_GUIDE.md](SEEDING_GUIDE.md) for database seeding help
- Check [DOCKER_SIMPLE_SETUP.md](DOCKER_SIMPLE_SETUP.md) for Docker setup
- Open an issue on GitHub
- Contact the maintainers

## 📊 Database Schema

### Key Models

**CustomUser**: Extends Django's AbstractUser with mobile number
**Food**: Food categories (Gujarati, Punjabi, etc.)
**FoodDetails**: Individual food items with price, stock, images
**Orders**: Customer orders with payment and delivery status
**OrderDetails**: Items in each order with quantity and delivery status
**Payment**: Payment records with Razorpay integration

## 🔒 Security

- Secret keys stored in environment variables
- CSRF protection enabled
- SQL injection prevention via ORM
- XSS protection in templates
- Secure password hashing
- Payment signature verification
- Session security

## 📈 Performance Optimization

- Database query optimization with select_related and prefetch_related
- Static file compression with WhiteNoise
- Efficient database indexing
- Connection pooling
- Caching strategies (can be extended)

## 🚀 Future Enhancements

- [ ] Email notifications for order updates
- [ ] SMS notifications
- [ ] Review and rating system
- [ ] Advanced search and filters
- [ ] Order history for customers
- [ ] Analytics dashboard for admins
- [ ] Multi-language support
- [ ] Push notifications
- [ ] Loyalty program
- [ ] Discount coupons

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Lakhman** - [@lakhman108](https://github.com/lakhman108)

## 🙏 Acknowledgments

- Django Framework
- Django REST Framework
- Razorpay Payment Gateway
- PostgreSQL Database
- Docker Community
- All contributors

## 📞 Support

For support, email plakhman@icloud.com or open an issue on GitHub.

---

<div align="center">
  Made with ❤️ by <a href="https://github.com/lakhman108">Lakhman</a>
</div>
