# Peepalytics Test API

Backend infrastructure for the Peepalytics test application, built with Django Rest Framework and Python 3.12.

## 🛠 Tech Stack

-   Python 3.12
-   Django Rest Framework
-   PostgreSQL
-   Square Payment Integration

## 🚀 Quick Start

### Prerequisites

-   Python 3.12
-   PostgreSQL
-   Virtual Environment (recommended)

### Installation

1. Clone the repository
   bash
   git clone <repository-url>
   cd peepalytics-test

2. Create and activate virtual environment

Windows:
python -m venv venv
venv\Scripts\activate

Unix or MacOS:
python -m venv venv
source venv/bin/activate

3. Install dependencies

pip install -r requirements.txt

4. Set up environment variables
   Create a `.env` file in the root directory with the following variables:

DEBUG=False
SECRET_KEY=your_secret_key
DATABASE_URL=postgres://user:password@localhost:5432/db_name
SQUARE_ACCESS_TOKEN=your_square_access_token
SQUARE_ENVIRONMENT=sandbox # or production

5. Run database migrations
   python manage.py makemigrations

python manage.py migrate

6. Start the development server
   python manage.py runserver

The API will be available at `http://localhost:8000`

## 🧪 Testing

Run the test suite using:
python manage.py test

## 📚 API Documentation

-   Local Swagger Documentation: `http://localhost:8000/swagger/`
-   Live API Documentation: [https://peepalytics-test.onrender.com/swagger/](https://peepalytics-test.onrender.com/swagger/)

## 🔑 API Endpoints

-   **Authentication**

    -   POST `/api/register/` - User registration
    -   POST `/api/login/` - User login

-   **Payments**
    -   GET `/api/payment/` - Retrieve payment details
    -   POST `/api/payment/` - Create new payment
    -   POST `/api/webhook/` - Square payment webhook

## 🚀 Deployment

The API is currently deployed on Render:
[https://peepalytics-test.onrender.com](https://peepalytics-test.onrender.com)

### Business Logic Assumptions

-   Users can only view their own payment history
-   Failed payments are automatically retried 3 times
-   Webhook notifications are processed asynchronously
-   Payment refunds must be processed within 30 days
-   All prices are in USD

### Frontend Integration

-   Frontend is served from a different domain
-   Frontend handles token storage and renewal
-   Supports modern browsers (Chrome 80+, Firefox 75+, Safari 13+)

-   **API Usage**
    -   All amounts are in cents (smallest currency unit)
    -   Dates are in ISO 8601 format
    -   Rate limiting: 100 requests per minute per user
