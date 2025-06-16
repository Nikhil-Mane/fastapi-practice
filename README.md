# Custom API Gateway

A FastAPI-based API Gateway with rate limiting, authentication, and request size validation.

## Features

- Rate limiting with IP-based and API key-based restrictions
- JWT token authentication
- API key validation
- Request size limiting
- Concurrent request limiting
- Versioned API endpoints (v1 and v2)

## Setup

### 1. Virtual Environment Setup

#### Windows
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Verify activation (you should see (venv) in your terminal)
python --version
```

#### Linux/MacOS
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify activation (you should see (venv) in your terminal)
python --version
```

### 2. Install Dependencies
```bash
# Make sure you're in the project directory and virtual environment is activated
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the project root:
```env
SECRET_KEY=your-secret-key
API_KEY=your-api-key
```

## Running the Application

1. Make sure your virtual environment is activated:
   - Windows: `.\venv\Scripts\activate`
   - Linux/MacOS: `source venv/bin/activate`

2. Start the application:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### V1
- `GET /v1/public` - Public endpoint with IP-based rate limit (10/minute)
- `GET /v1/protected` - Protected endpoint with JWT authentication (5/minute)

### V2
- `GET /v2/data` - Protected endpoint with API key validation

## Deactivating Virtual Environment

When you're done working on the project, you can deactivate the virtual environment:
```bash
deactivate
```