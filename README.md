# Django Notes App

A Django-based note-taking web application with user authentication, CRUD operations, image uploads, JWT-based REST APIs, password reset using Gmail SMTP and OTP verification, and PostgreSQL database support.

## Features

- User registration and login/logout
- Password validation using Regex
- Create, view, edit, and delete notes
- User-specific notes
- Image upload for notes
- Images stored using AWS S3
- Password reset using Gmail SMTP and OTP verification
- PostgreSQL database
- REST API using Django REST Framework
- JWT authentication with refresh token and logout/blacklisting support
- Swagger/OpenAPI API documentation
- Dockerized local development with Docker Compose
- Deployed on AWS EC2 using Nginx and Gunicorn
- Also configured for deployment on Render

## Tech Stack

- **Backend:** Python, Django
- **Frontend:** HTML, CSS, JavaScript
- **API:** Django REST Framework
- **Authentication:** JWT
- **API Documentation:** drf-spectacular / Swagger UI
- **Database:** PostgreSQL
- **Storage:** AWS S3
- **Email:** Gmail SMTP
- **Containerization:** Docker, Docker Compose
- **Deployment:** AWS EC2
- **Web Server:** Nginx
- **Application Server:** Gunicorn

## Project Structure

```
SI_Django_Notes_Task/
â”œâ”€â”€ api/
â”‚   â”œâ”€â”€ migrations/
â”‚   â”œâ”€â”€ serializers.py
â”‚   â”œâ”€â”€ urls.py
â”‚   â””â”€â”€ views.py
â”œâ”€â”€ config/
â”‚   â”œâ”€â”€ settings.py
â”‚   â”œâ”€â”€ urls.py
â”‚   â”œâ”€â”€ wsgi.py
â”‚   â””â”€â”€ asgi.py
â”œâ”€â”€ notes/
â”‚   â”œâ”€â”€ migrations/
â”‚   â”œâ”€â”€ templates/
â”‚   â”œâ”€â”€ models.py
â”‚   â”œâ”€â”€ urls.py
â”‚   â””â”€â”€ views.py
â”œâ”€â”€ media/
â”œâ”€â”€ staticfiles/
â”œâ”€â”€ manage.py
â”œâ”€â”€ requirements.txt
â”œâ”€â”€ Dockerfile
â”œâ”€â”€ compose.yaml
â”œâ”€â”€ .dockerignore
â”œâ”€â”€ build.sh
â””â”€â”€ .gitignore
```

## Local Setup

### Option 1: Run with Docker

Docker Compose runs the Django application and PostgreSQL database as separate containers.

```
Browser â†“ Django container â†“ PostgreSQL container â†“ postgres_data volume
```

#### 1. Clone the Repository
```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd SI_Django_Notes_Task
```

#### 2. Configure Environment Variables
Create a `.env` file in the project root:

```env
SECRET_KEY=your_secret_key
DEBUG=True
POSTGRES_DB=notesdb
POSTGRES_USER=notesuser
POSTGRES_PASSWORD=your_local_database_password
DATABASE_HOST=db
DATABASE_PORT=5432
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_gmail_address
EMAIL_HOST_PASSWORD=your_gmail_app_password
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_STORAGE_BUCKET_NAME=your_bucket_name
AWS_S3_REGION_NAME=ap-south-1
```

> **Important:** Do not commit `.env` or any credentials to GitHub.

#### 3. Build and Start the Containers
```bash
docker compose up -d --build
```
This starts:
- Django application container
- PostgreSQL database container

#### 4. Apply Migrations
```bash
docker compose exec web python manage.py migrate
```

#### 5. Create an Admin User
```bash
docker compose exec web python manage.py createsuperuser
```

#### 6. Open the Application
[http://localhost:8000/](http://localhost:8000/)

#### Useful Docker Commands

- **Check Running Containers:**
  ```bash
  docker compose ps
  ```
- **View Django Logs:**
  ```bash
  docker compose logs web
  ```
- **View PostgreSQL Logs:**
  ```bash
  docker compose logs db
  ```
- **Stop the Containers:**
  ```bash
  docker compose down
  ```
- **Start the Containers Again:**
  ```bash
  docker compose up -d
  ```
- **Rebuild the Django Image:**
  ```bash
  docker compose up -d --build
  ```

> `docker compose down` removes the containers but keeps the PostgreSQL named volume. Avoid `docker compose down -v` unless you intentionally want to delete the local PostgreSQL data.

---

### Local Setup Without Docker

A Python virtual environment can also be used for local development.

#### 1. Create and Activate a Virtual Environment

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Configure Environment Variables
Create the required `.env` file as described above.

#### 4. Apply Migrations
```bash
python manage.py migrate
```

#### 5. Run the Development Server
```bash
python manage.py runserver
```

Open: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## REST API

The project includes a REST API built using Django REST Framework (DRF).

The API uses JWT authentication for protected endpoints.

### Authentication Endpoints

| Method | Endpoint | Description | Authentication |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/register/` | Register a new user | No |
| `POST` | `/api/token/` | Obtain JWT access and refresh tokens | No |
| `POST` | `/api/token/refresh/` | Generate a new access token | No |
| `POST` | `/api/token/logout/` | Logout and blacklist the refresh token | JWT |

### Notes Endpoints

| Method | Endpoint | Description | Authentication |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/notes/` | Get the logged-in user's notes | JWT |
| `POST` | `/api/notes/` | Create a new note | JWT |
| `GET` | `/api/notes/<id>/` | Get a specific note | JWT |
| `PUT` | `/api/notes/<id>/` | Update a note | JWT |
| `PATCH` | `/api/notes/<id>/` | Partially update a note | JWT |
| `DELETE` | `/api/notes/<id>/` | Delete a note | JWT |

### Password Reset Endpoints

The password reset flow uses Gmail SMTP and OTP verification.

| Method | Endpoint | Description | Authentication |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/forgot-password/` | Request a password-reset OTP | No |
| `POST` | `/api/verify-otp/` | Verify the OTP sent to the user's email | No |
| `POST` | `/api/reset-password/` | Set a new password after OTP verification | No |

---

### JWT Authentication

After obtaining an access token from `/api/token/`, include it in the request header:

```http
Authorization: Bearer <access_token>
```

- The refresh token can be used with `/api/token/refresh/` to obtain a new access token.
- The logout endpoint blacklists the refresh token.

---

### API Documentation

Interactive Swagger documentation is available at: `/api/docs/`  
The OpenAPI schema is available at: `/api/schema/`

Swagger UI can be used to explore the available endpoints, request parameters, authentication requirements, responses, and HTTP status codes.

---

## Password Reset

The application uses Gmail SMTP for password-reset OTP delivery.

The general flow is:
```
User requests password reset â†“ OTP generated â†“ OTP sent through Gmail SMTP â†“ User verifies OTP â†“ User sets a new password
```

Gmail credentials should be stored in `.env` and never committed to version control.

---

## AWS S3 Storage

Note images are stored using Amazon S3 through `django-storages` and `boto3`.

The required AWS configuration is provided through environment variables:

```env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_STORAGE_BUCKET_NAME=your_bucket_name
AWS_S3_REGION_NAME=ap-south-1
```

> **Important:** Never commit AWS credentials to GitHub.

---

## Deployment

The application is deployed on AWS EC2 using:
```
Nginx â†’ Gunicorn â†’ Django
```

Gunicorn and Nginx are configured as system services, so the application continues running after the SSH terminal is closed.

For production:
```env
DEBUG=False
```

The production deployment uses its configured PostgreSQL database and existing AWS S3 storage.

### Updating the EC2 Deployment

Changes pushed to GitHub are not automatically deployed to EC2.

After pushing new changes:
```bash
cd ~/SI_Django_Notes_Task
git pull
sudo systemctl restart notes
```

If dependencies were changed:
```bash
cd ~/SI_Django_Notes_Task
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart notes
```

---

## Security Notes

- Keep `.env` out of version control.
- Never expose Gmail credentials or AWS access keys.
- Never expose database passwords.
- Never expose the EC2 `.pem` private key.
- Use `DEBUG=False` in production.
- Use JWT authentication for protected API endpoints.
- Restrict access to user-owned notes through authentication and ownership checks.
- Do not use `docker compose down -v` unless you intentionally want to delete the local PostgreSQL data volume.
