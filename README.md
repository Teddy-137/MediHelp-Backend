# MediHelp Backend

MediHelp is a comprehensive healthcare platform that connects patients with medical resources, symptom checking, doctor consultations, and educational content.

## 🌟 Features

- **User Authentication**: Secure JWT-based authentication system
- **Symptom Checking**: AI-powered symptom analysis and condition suggestions
- **Doctor Consultations**: Schedule teleconsultations with specialized doctors
- **First Aid Information**: Quick access to emergency first aid procedures
- **Educational Content**: Health articles and videos
- **Clinic Locator**: Find nearby clinics with geospatial search
- **Skin Condition Diagnosis**: AI-powered skin condition analysis

## 🛠️ Tech Stack

- **Framework**: Django 5.2 with Django REST Framework
- **Authentication**: JWT (Simple JWT)
- **Database**:
  - Development: SQLite
  - Production: PostgreSQL (on Render)
- **API Documentation**: drf-spectacular (OpenAPI)
- **AI Integration**: Google Gemini API for symptom analysis
- **Static Files**: WhiteNoise for serving static files
- **Deployment**: Render (PaaS)

## 📋 Prerequisites

- Python 3.10+
- Google Gemini API key (for AI features)
- Git (for version control)
- GitHub account (for deployment to Render)

## 🚀 Installation

### Local Development

1. **Clone the repository**

```bash
git clone https://github.com/Teddy-137/MediHelp-Backend.git
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
```

5. **Run migrations**

```bash
python manage.py migrate
```

6. **Create a superuser**

```bash
python manage.py createsuperuser
```

7. **Run the development server**

```bash
python manage.py runserver
```

8. **Populate db**
```bash
python manage.py loaddata symptoms/fixtures/initial_data.json
python manage.py loaddata education/fixtures/initial_data.json
python manage.py loaddata firstaid/fixtures/initial_data.json
```

The API will be available at http://localhost:8000/api/

### Deployment on Render

1. **Fork or clone this repository to your GitHub account**

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
   - The first deployment may take a few minutes

7. **Load Initial Data (Optional)**
   - After deployment, you can load initial data using the Render shell:
     ```bash
     python manage.py loaddata symptoms/fixtures/initial_data.json
     python manage.py loaddata education/fixtures/initial_data.json
     python manage.py loaddata firstaid/fixtures/initial_data.json
     ```

Your API will be available at `https://medihelp-backend.onrender.com/api/`

## 📚 API Documentation

API documentation is available at:
- Swagger UI: http://localhost:8000/schema/swagger-ui/
- ReDoc: http://localhost:8000/schema/redoc/

## 🧪 Testing API Endpoints

The project includes an `api.http` file that can be used with REST Client extensions (like the one for VS Code) to test all endpoints. The file contains examples for:

- Authentication (register, login, refresh token)
- Symptom checking
- Doctor consultations
- First aid information
- Educational content
- Core system endpoints

## 📱 API Endpoints

### Authentication

- `POST /api/auth/register/` - Register a new user
- `POST /api/auth/login/` - Login and get tokens
- `POST /api/auth/logout/` - Logout (blacklist token)
- `POST /api/auth/token/refresh/` - Refresh access token

### Health/Symptoms

- `GET /api/health/symptoms/` - List all symptoms
- `GET /api/health/conditions/` - List all conditions
- `POST /api/health/checks/` - Create a symptom check
- `GET /api/health/checks/` - List user's symptom checks

### Doctors

- `POST /api/doctors/register/` - Register as a doctor
- `GET /api/doctors/profiles/` - List all doctor profiles
- `POST /api/doctors/availability/` - Create availability slot
- `GET /api/doctors/availability/` - List availability slots
- `POST /api/doctors/teleconsults/` - Create teleconsultation
- `GET /api/doctors/teleconsults/` - List teleconsultations

### First Aid

- `GET /api/firstaid/` - List first aid guides and remedies
- `GET /api/firstaid/{id}/` - Get specific first aid guide
- `GET /api/firstaid/remedies/{id}/` - Get specific home remedy

### Education

- `GET /api/content/articles/` - List health articles
- `GET /api/content/videos/` - List educational videos

### Core

- `GET /api/core/healthz/` - Check server status
- `GET /api/core/metrics/` - Get server metrics (admin only)

## 🏗️ Project Structure

```
MediHelp-Backend/
├── accounts/          # User authentication and profiles
├── symptoms/          # Symptom checking and health conditions
├── doctors/           # Doctor profiles and teleconsultations
├── firstaid/          # Emergency first aid information
├── education/         # Health articles and educational videos
├── skin_diagnosis/    # Skin condition analysis
├── core/              # Core functionality and utilities
├── medihelp/          # Project settings and main URLs
├── api.http           # API testing file
├── requirements.txt   # Project dependencies
├── build.sh           # Build script for Render deployment
├── render.yaml        # Render configuration file
└── runtime.txt        # Python version specification
```

## 🔒 Security Notes

- The project uses JWT for authentication with access and refresh tokens
- Access tokens expire after 60 minutes
- Refresh tokens are valid for 7 days and are rotated on use
- Rate limiting is implemented for sensitive endpoints

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Contact

Your Name - your.email@example.com

Project Link: [https://github.com/yourusername/MediHelp-Backend](https://github.com/yourusername/MediHelp-Backend)
