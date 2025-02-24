# HostHunt Backend

Django Rest Framework-based backend for the HostHunt platform, featuring Celery task automation and Redis caching, deployed on AWS.

## 🏗 Architecture

- Django Rest Framework API
- Celery for async tasks
- Redis for caching and WebSocket
- AWS RDS (PostgreSQL)
- AWS S3 for storage
- Docker containerization

## 🚀 Key Features

- RESTful API endpoints for booking management
- Real-time notifications using WebSocket
- Automated email notifications via Celery
- Secure payment processing with Stripe
- Google Places API integration
- OpenAI API integration for property descriptions
- AWS S3 for image storage
- Comprehensive admin dashboard

## 🛠 Deployment Setup

1. Clone the repository:
```bash
git clone <backend-repository-url>
cd hosthunt-backend
```

2. Create `.env` file in HostHunt_Backend directory:
```env
DEBUG=False
SECRET_KEY=your_secret_key
DATABASE_URL=your_aws_rds_url
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_STORAGE_BUCKET_NAME=your_s3_bucket_name
STRIPE_SECRET_KEY=your_stripe_secret_key
OPENAI_API_KEY=your_openai_api_key
GOOGLE_PLACES_API_KEY=your_google_api_key
REDIS_HOST=redis
REDIS_PORT=6379
CELERY_BROKER_URL=redis://redis:6379/0
```

3. Set up SSL certificates:
```bash
# Install certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com
```

4. Start the application:
```bash
docker-compose up -d
```

## 🐳 Docker Services

- Backend (Django application)
- Celery worker
- Celery beat
- Redis

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register/`: User registration
- `POST /api/auth/login/`: User login
- `POST /api/auth/google/`: Google OAuth

### Properties
- `GET /api/properties/`: List properties
- `POST /api/properties/`: Create property
- `GET /api/properties/<id>/`: Property details
- `PUT /api/properties/<id>/`: Update property
- `DELETE /api/properties/<id>/`: Delete property

### Bookings
- `POST /api/bookings/`: Create booking
- `GET /api/bookings/`: List user bookings
- `GET /api/bookings/<id>/`: Booking details

### Payments
- `POST /api/payments/create-intent/`: Create payment intent
- `POST /api/payments/confirm/`: Confirm payment

## 🔄 Background Tasks

Celery handles:
- Email notifications
- Payment reminders
- Booking status updates
- Property analytics calculations

## 🔍 Monitoring

- Application logs available in Docker logs
- Celery task monitoring
- Redis cache monitoring

## 🛡 Security

- JWT authentication
- SSL/TLS encryption
- AWS security groups
- API rate limiting
- Input validation and sanitization

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

