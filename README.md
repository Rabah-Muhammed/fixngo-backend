# Home Service Booking Application(FIXNGO) - Backend

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Django REST](https://img.shields.io/badge/django%20rest-ff1709?style=for-the-badge&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![WebSockets](https://img.shields.io/badge/WebSocket-000000?style=for-the-badge&logo=websocket&logoColor=white)

A robust backend system for a home service booking platform built with Django REST Framework and WebSockets, featuring user authentication, service management, booking system, and real-time chat.

---

## 🚀 Features

### 🔐 User Authentication System
- Email verification with OTP
- JWT token authentication
- Google OAuth integration
- Password reset functionality

### 🛠️ Service Management
- Service categories and listings
- Worker profiles with skills and availability
- Service area filtering

### 📅 Booking System
- Slot-based scheduling
- Booking status workflow (pending → processing → started → completed)
- PayPal payment integration
- Worker wallet system

### 💬 Real-Time Communication
- WebSocket-based chat system
- Support for text and image messages
- Typing indicators
- Message read receipts
- Notification system

### 🌟 Review System
- Rating and feedback for services
- Worker performance metrics

---

## 🧱 System Architecture

home-service-backend/ ├── api/ # Core application │ ├── models.py # Database models │ ├── serializers.py # Data serializers │ ├── views.py # API endpoints │ ├── urls.py # URL routing │ ├── consumers.py # WebSocket handlers │ └── utils.py # Helper functions ├── config/ # Project configuration │ ├── settings.py # Django settings │ ├── urls.py # Root URL routing │ └── asgi.py # ASGI configuration └── chat/ # Chat application ├── models.py # Chat models ├── consumers.py # Chat WebSocket handlers └── routing.py # WebSocket routing

pgsql
Copy
Edit

---

## 📡 API Documentation

### 🔐 Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/signup/` | POST | User registration with email verification |
| `/api/verify-otp/` | POST | Verify email with OTP |
| `/api/login/` | POST | JWT token authentication |
| `/api/login-with-google/` | POST | Google OAuth authentication |
| `/api/request-reset-password/` | POST | Initiate password reset |
| `/api/reset-password/` | POST | Complete password reset |

### 🛠️ Services & Workers

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/services/` | GET | List all available services |
| `/api/services/<id>/` | GET | Get service details |
| `/api/services/<id>/workers/` | GET | List workers for a service |
| `/api/worker/<id>/` | GET | Get worker profile |

### 📅 Bookings

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/bookings/` | POST | Create new booking |
| `/api/bookings/<id>/` | GET | Get booking details |
| `/api/user/bookings/` | GET | List user's bookings |
| `/api/bookings/cancel/<id>/` | PATCH | Cancel a booking |
| `/api/paypal/create-order/` | POST | Initiate PayPal payment |

### 💬 Chat System

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat/start-chat/` | POST | Start new chat room |
| `/chat/<chat_id>/messages/` | GET | Get chat messages |
| `/chat/<chat_id>/send-message/` | POST | Send new message |
| `/chat/rooms/` | GET | List user's chat rooms |
| `ws/chat/<room_id>/` | WebSocket | Real-time chat connection |

---

## ⚙️ Installation & Setup

### 🔧 Prerequisites

- Python 3.9+
- PostgreSQL
- Redis (for WebSockets and caching)

### 🛠️ Step-by-step Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/home-service-backend.git
cd home-service-backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # For Linux/Mac
venv\Scripts\activate     # For Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file with the following environment variables
echo "SECRET_KEY=your_django_secret_key
DATABASE_URL=postgres://user:password@localhost:5432/dbname
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_CLIENT_SECRET=your_paypal_secret
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_secret
EMAIL_HOST=your_smtp_host
EMAIL_PORT=587
EMAIL_HOST_USER=your_email
EMAIL_HOST_PASSWORD=your_email_password" > .env

# Run migrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser

# Start the Django development server
python manage.py runserver

# Start Redis server (in a separate terminal)
redis-server

# Start ASGI server (in a new terminal)
daphne config.asgi:application
