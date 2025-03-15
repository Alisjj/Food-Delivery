# Vega Food Delivery API Documentation

## Overview

The Vega Food Delivery API is a Django-based web service that allows users to order food from nearby restaurants, track deliveries, and manage their orders. This documentation provides details on the project structure, key components, and how to use the API.

## Project Structure

The project is organized into several Django apps:

-   **users**: Handles user authentication, registration, and profile management
-   **restaurants**: Manages restaurant data, menu items, and courier information
-   **orders**: Handles order processing, tracking, and delivery management
-   **config**: Core configuration and settings

## Setup and Installation

### Prerequisites

-   Docker and Docker Compose
-   Python 3.12+

### Installation Steps

1. Clone the repository:

    ```bash
    git clone https://github.com/alisjj/AliyuSani_Vega_FoodDelivery.git
    cd AliyuSani_Vega_FoodDelivery
    ```

2. Create a .env.dev file in the app directory:

    ```
    DEBUG=1
    SECRET_KEY=your-secret-key
    DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]
    CELERY_BROKER_URL=redis://redis:6379
    CELERY_RESULT_BACKEND=redis://redis:6379
    ```

3. Start the application with Docker Compose:

    ```bash
    docker-compose up -d
    ```

4. Generate test data (optional):

    ```bash
    docker-compose exec web python manage.py generate_test_data --clear
    ```

## Core Components

### User Management

The users app provides account management features:

-   User registration with email verification
-   JWT authentication
-   Password reset functionality
-   Profile management with delivery location tracking

### Menu and Restaurant System

The restaurants app manages food items and restaurant information:

-   Restaurant listings with location data
-   Food items categorized by type (appetizer, main course, dessert, etc.)
-   Courier management and availability tracking

### Order Processing

The orders app handles the order lifecycle:

-   Creating new orders
-   Assigning orders to nearby restaurants and available couriers
-   Order status tracking (PENDING, PREPARING, DELIVERING, DELIVERED, CANCELLED)
-   Order history and details

### Background Tasks

The project uses Celery with Redis for background processing:

-   Automatic order status updates
-   Scheduled delivery time calculations
-   Email notifications

## API Endpoints

### Authentication

| Endpoint                            | Method | Description            |
| ----------------------------------- | ------ | ---------------------- |
| `/api/auth/signup/`                 | POST   | Register a new user    |
| `/api/auth/login/`                  | POST   | Obtain JWT token       |
| `/api/auth/verify-email/`           | POST   | Verify user email      |
| `/api/auth/password-reset/`         | POST   | Request password reset |
| `/api/auth/password-reset/confirm/` | POST   | Confirm password reset |

### Restaurants and Menu

| Endpoint                            | Method | Description           |
| ----------------------------------- | ------ | --------------------- |
| `/api/restaurants/menu-items/`      | GET    | List all menu items   |
| `/api/restaurants/menu-items/<id>/` | GET    | Get menu item details |

### Orders

| Endpoint                          | Method | Description        |
| --------------------------------- | ------ | ------------------ |
| `/api/orders/orders/`             | GET    | List user orders   |
| `/api/orders/orders/`             | POST   | Create a new order |
| `/api/orders/orders/<id>/`        | GET    | Get order details  |
| `/api/orders/orders/<id>/cancel/` | POST   | Cancel an order    |
| `/api/orders/orders/<id>/track/`  | GET    | Track order status |
| `/api/orders/orders/history/`     | GET    | View order history |

## Data Models

### User

-   Username
-   Email (with verification)
-   Password
-   Delivery location details
-   Account status

### Restaurant

-   Name
-   Address
-   Geographical coordinates
-   Availability status

### Courier

-   Name
-   Restaurant association
-   Phone number
-   Availability status

### FoodItem

-   Name
-   Description
-   Price
-   Category
-   Availability

### Order

-   User
-   Restaurant
-   Courier
-   Status
-   Order time
-   Total price
-   Estimated delivery time

### OrderItem

-   Order
-   Food item
-   Quantity
-   Price

## Testing

Run tests using Django's test framework:

```bash
docker-compose exec web python manage.py test
```

## Development Tools

### Generate Test Data

The project includes a custom management command to generate test data:

```bash
python manage.py generate_test_data [options]
```

Options:

-   `--users`: Number of users to create (default: 5)
-   `--restaurants`: Number of restaurants to create (default: 3)
-   `--fooditems`: Number of food items to create (default: 15)
-   `--clear`: Clear existing data before generating new data

## Technical Stack

-   **Backend**: Django 5.0, Django REST Framework 3.15
-   **Authentication**: JWT (djangorestframework_simplejwt)
-   **Database**: PostgreSQL (configured) / SQLite (development)
-   **Task Queue**: Celery 5.4 with Redis 5.0
-   **Containerization**: Docker and Docker Compose
