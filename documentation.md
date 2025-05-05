# MediHelp Backend Documentation

## Overview

MediHelp is a comprehensive healthcare platform that connects patients with medical resources, symptom checking, doctor consultations, and educational content. This documentation provides detailed information about the backend API, architecture, and implementation.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [API Documentation](#api-documentation)
- [Authentication](#authentication)
- [Core Modules](#core-modules)
- [Deployment](#deployment)
- [Testing](#testing)
- [Security](#security)

## Features

- **User Authentication**: Secure JWT-based authentication system
- **Symptom Checking**: AI-powered symptom analysis and condition suggestions
- **Doctor Consultations**: Schedule teleconsultations with specialized doctors
- **First Aid Information**: Quick access to emergency first aid procedures
- **Educational Content**: Health articles and videos
- **Clinic Locator**: Find nearby clinics with geospatial search
- **Skin Condition Diagnosis**: AI-powered skin condition analysis
- **Chatbot**: AI-powered medical assistant for general health queries

## Tech Stack

- **Framework**: Django 5.2 with Django REST Framework
- **Authentication**: JWT (Simple JWT)
- **Database**:
  - Development: SQLite
  - Production: PostgreSQL
- **API Documentation**: drf-spectacular (OpenAPI)
- **AI Integration**: Google Gemini API for symptom analysis and chatbot
- **Static Files**: WhiteNoise for serving static files
- **Deployment**: Render (PaaS) or Railway

## Installation

### Prerequisites

- Python 3.10+
- Google Gemini API key (for AI features)
- Git (for version control)

### Local Development Setup

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/MediHelp-Backend.git
cd MediHelp-Backend
```

2. **Create and activate a virtual environment**

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

Create a `.env` file in the project root with the following:

```
GEMINI_API_KEY=your_gemini_api_key
SECRET_KEY=your_secret_key
DEBUG=True
ENVIRONMENT=development
```

5. **Run migrations**

```bash
python manage.py migrate
```

6. **Create a superuser**

```bash
python manage.py createsuperuser
```

7. **Load initial data**

```bash
python manage.py loaddata symptoms/fixtures/initial_data.json
python manage.py loaddata education/fixtures/initial_data.json
python manage.py loaddata firstaid/fixtures/initial_data.json
```

8. **Run the development server**

```bash
python manage.py runserver
```

The API will be available at http://localhost:8000/api/

## API Documentation

API documentation is available at:
- Swagger UI: http://localhost:8000/schema/swagger-ui/
- ReDoc: http://localhost:8000/schema/redoc/

## Authentication

The API uses JWT (JSON Web Tokens) for authentication with the following endpoints:

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register a new user |
| POST | `/api/auth/login/` | Login and get tokens |
| POST | `/api/auth/logout/` | Logout (blacklist token) |
| POST | `/api/auth/token/refresh/` | Refresh access token |
| GET | `/api/auth/me/` | Get user profile |
| PATCH | `/api/auth/me/` | Update user profile |

### JWT Configuration

- Access tokens expire after 60 minutes
- Refresh tokens are valid for 7 days and are rotated on use
- Token blacklisting is enabled for logout functionality

### Authentication Example

```python
import requests

# Register a new user
register_data = {
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+251912345678",
    "date_of_birth": "1990-01-01",
    "password": "SecurePassword123!",
    "confirm_password": "SecurePassword123!"
}
register_response = requests.post("http://localhost:8000/api/auth/register/", json=register_data)

# Login to get tokens
login_data = {
    "email": "user@example.com",
    "password": "SecurePassword123!"
}
login_response = requests.post("http://localhost:8000/api/auth/login/", json=login_data)
tokens = login_response.json()

# Use access token for authenticated requests
headers = {
    "Authorization": f"Bearer {tokens['access']}"
}
profile_response = requests.get("http://localhost:8000/api/auth/me/", headers=headers)
```

## Core Modules

### Accounts

Handles user authentication, registration, and profile management.

### Symptoms

Provides symptom checking and health condition information:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health/symptoms/` | List all symptoms |
| GET | `/api/health/conditions/` | List all conditions |
| POST | `/api/health/checks/` | Create a symptom check |
| GET | `/api/health/checks/` | List user's symptom checks |

### Doctors

Manages doctor profiles, availability, and teleconsultations:

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/doctors/register/` | Register as a doctor |
| GET | `/api/doctors/profiles/` | List all doctor profiles |
| POST | `/api/doctors/availability/` | Create availability slot |
| GET | `/api/doctors/availability/` | List availability slots |
| POST | `/api/doctors/teleconsults/` | Create teleconsultation |
| GET | `/api/doctors/teleconsults/` | List teleconsultations |

### First Aid

Provides emergency first aid information:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/firstaid/` | List first aid guides and remedies |
| GET | `/api/firstaid/{id}/` | Get specific first aid guide |
| GET | `/api/firstaid/remedies/{id}/` | Get specific home remedy |

### Education

Manages health articles and educational videos:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/content/articles/` | List health articles |
| GET | `/api/content/videos/` | List educational videos |

### Skin Diagnosis

Provides AI-powered skin condition analysis:

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/skin-diagnosis/` | Submit image for diagnosis |

### Chatbot

Provides an AI-powered medical assistant:

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat/interact/` | Interact with the chatbot |

### Clinics

Manages clinic information and geospatial search:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/clinics/` | List all clinics |
| GET | `/api/clinics/{id}/` | Get specific clinic |
| GET | `/api/clinics/nearby/` | Find nearby clinics |

### Core

Provides system-level endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/core/healthz/` | Check server status |
| GET | `/api/core/metrics/` | Get server metrics (admin only) |

## Deployment

### Deployment on Render

1. **Fork or clone the repository to your GitHub account**

2. **Sign up for Render**
   - Go to [render.com](https://render.com/) and sign up for an account
   - Connect your GitHub account

3. **Create a new Web Service**
   - Click "New +" and select "Web Service"
   - Connect your GitHub repository
   - Give your service a name (e.g., "medihelp-backend")
   - Select "Python 3" as the runtime
   - Set the build command: `./build.sh`
   - Set the start command: `gunicorn medihelp.wsgi:application`

4. **Set Environment Variables**
   - In the "Environment" section, add the following variables:
     - `SECRET_KEY`: Generate a secure random string
     - `DEBUG`: Set to "False"
     - `ENVIRONMENT`: Set to "production"
     - `GEMINI_API_KEY`: Your Gemini API key
     - `RENDER`: Set to "True"

5. **Add a PostgreSQL Database**
   - Click "New +" and select "PostgreSQL"
   - Give your database a name (e.g., "medihelp-db")
   - Render will automatically link the database to your web service

6. **Deploy**
   - Click "Create Web Service"
   - Render will automatically deploy your application

### Deployment on Railway

1. **Create a Railway account**
   - Go to [railway.app](https://railway.app/) and sign up

2. **Create a new project**
   - Click "New Project" and select "Deploy from GitHub repo"
   - Connect your GitHub repository

3. **Configure the project**
   - Railway will automatically detect the `railway.json` configuration
   - Add the required environment variables:
     - `SECRET_KEY`: Generate a secure random string
     - `DEBUG`: Set to "False"
     - `ENVIRONMENT`: Set to "production"
     - `GEMINI_API_KEY`: Your Gemini API key

4. **Add a PostgreSQL database**
   - Click "New" and select "Database" > "PostgreSQL"
   - Railway will automatically link the database to your service

5. **Deploy**
   - Railway will automatically deploy your application

## Testing

### API Testing with REST Client

The project includes an `api.http` file that can be used with REST Client extensions (like the one for VS Code) to test all endpoints. The file contains examples for all API endpoints with proper request bodies and authentication.

### Running Tests

```bash
python manage.py test
```

## Security

- JWT authentication with token expiration and rotation
- Rate limiting for sensitive endpoints:
  - Symptom checks: 10 per hour
  - First aid: 60 per minute
  - Skin diagnosis: 5 per hour
  - Chatbot: 10 per minute
- CORS configuration for frontend integration
- Environment variable management for sensitive credentials
- Database connection pooling in production

## Project Structure

```
MediHelp-Backend/
├── accounts/          # User authentication and profiles
├── symptoms/          # Symptom checking and health conditions
├── doctors/           # Doctor profiles and teleconsultations
├── firstaid/          # Emergency first aid information
├── education/         # Health articles and educational videos
├── skin_diagnosis/    # Skin condition analysis
├── chatbot/           # AI-powered medical assistant
├── clinics/           # Clinic information and geospatial search
├── core/              # Core functionality and utilities
├── medihelp/          # Project settings and main URLs
├── api.http           # API testing file
├── requirements.txt   # Project dependencies
├── build.sh           # Build script for Render deployment
├── render.yaml        # Render configuration file
├── railway.json       # Railway configuration file
└── runtime.txt        # Python version specification
```

## AI Integration

The project uses Google's Gemini API for several AI-powered features:

1. **Symptom Analysis**: Analyzes user-reported symptoms to suggest possible conditions and recommendations
2. **Chatbot**: Provides conversational medical assistance for general health queries
3. **Skin Diagnosis**: Analyzes uploaded images to identify potential skin conditions

### AI Configuration

The Gemini API key must be set in the environment variables:

```
GEMINI_API_KEY=your_gemini_api_key
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.