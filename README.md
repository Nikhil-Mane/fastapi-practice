# FastAPI E-commerce Platform

A modern, production-ready e-commerce platform built with FastAPI, PostgreSQL, and async background processing. Features include user authentication, product catalog, shopping cart, order management, admin controls, and real-time order processing.

---

## Features

- User registration, login, JWT authentication, and role-based access (user/admin)
- Product catalog with pagination, filtering, and admin CRUD
- Shopping cart for authenticated users
- Place orders (single product or from cart)
- Real-time async order processing (background worker)
- Order history for users
- Admin endpoints for managing users and orders
- Dockerized for easy deployment
- OpenAPI docs at `/docs`

---

## Architecture

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Frontend   │───▶│   FastAPI    │───▶│  PostgreSQL  │
│ (any client) │    │  E-commerce  │    │   Database   │
└──────────────┘    └──────────────┘    └──────────────┘
         │                  │
         ▼                  ▼
   ┌──────────────┐   ┌──────────────┐
   │  Background  │   │   Docker     │
   │   Worker     │   │   Compose    │
   └──────────────┘   └──────────────┘
```

---

## API Overview

### Authentication
- `POST /users/register` — Register a new user
- `POST /users/login` — Login and receive JWT token

### Products
- `GET /products/` — List products (pagination, filtering, search)
- `POST /products/` — Add product (admin only)
- `PUT /products/{id}` — Update product (admin only)
- `DELETE /products/{id}` — Delete product (admin only)

### Cart
- `POST /cart/add` — Add product to cart
- `GET /cart/` — View cart
- `POST /cart/remove` — Remove item from cart
- `POST /cart/clear` — Clear cart

### Orders
- `POST /orders/` — Place order for a single product
- `POST /orders/from_cart` — Place order for all items in cart
- `GET /orders/my` — View your order history
- `GET /orders/all` — List all orders (admin only)
- `GET /orders/user/{user_id}` — List orders for a user (admin only)

### Users (Admin)
- `GET /users/all` — List all users (admin only)
- `GET /users/{user_id}` — Get user by ID (admin only)

---

## Usage Examples

### Register & Login
```bash
curl -X POST http://localhost:8000/users/register -H "Content-Type: application/json" -d '{"username": "alice", "email": "alice@example.com", "password": "password"}'
curl -X POST http://localhost:8000/users/login -H "Content-Type: application/json" -d '{"username": "alice", "email": "alice@example.com", "password": "password"}'
```

### Browse Products
```bash
curl http://localhost:8000/products/?skip=0&limit=10&search=phone
```

### Add to Cart & Place Order
```bash
# Add to cart (requires JWT token)
curl -X POST http://localhost:8000/cart/add -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d '{"product_id": 1, "quantity": 2}'
# Place order from cart
curl -X POST http://localhost:8000/orders/from_cart -H "Authorization: Bearer <token>"
```

### Admin: Add Product
```bash
curl -X POST http://localhost:8000/products/ -H "Authorization: Bearer <admin_token>" -H "Content-Type: application/json" -d '{"name": "Laptop", "description": "High-end laptop", "price": 1200, "stock": 10}'
```

---

## Quick Start

### Prerequisites
- Docker Desktop (with Compose)
- Python 3.10+
- PostgreSQL running (or use Docker Compose)

### 1. Clone the repository
```bash
git clone <repo-url>
cd fastapi-practice
```

### 2. Build and start all services
```bash
docker-compose up --build
```

### 3. Access the API
- Main API: [http://localhost:8000](http://localhost:8000)
- API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Development

- Install dependencies: `pip install -r requirements.txt`
- Run locally: `uvicorn app.main:app --reload`
- Use Docker Compose for full stack: `docker-compose up --build`
- Run tests: `pytest`

---

## Configuration

- All config via environment variables (see `.env.example`)
- Example: `DATABASE_URL`, `LOG_LEVEL`, etc.

---

## License
MIT

---

## Contributors
- [Your Name Here]