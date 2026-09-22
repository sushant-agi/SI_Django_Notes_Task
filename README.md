# Django Notes App

A full-stack Django-based note-taking web application featuring user authentication, CRUD operations, image uploads, JWT-based REST APIs, password reset using Gmail SMTP and OTP verification, PostgreSQL database support, Redis caching, Docker containerization, and automated CI/CD deployment to AWS EC2.

---

## Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Local Setup with Docker](#local-setup-with-docker)
- [Redis Integration](#redis-integration)
  - [API Caching](#api-caching)
  - [Rate Limiting](#rate-limiting)
  - [OTP Storage](#otp-storage)
- [REST API Reference](#rest-api-reference)
  - [Authentication Endpoints](#authentication-endpoints)
  - [Notes Endpoints](#notes-endpoints)
  - [Password Reset Endpoints](#password-reset-endpoints)
  - [JWT Authentication](#jwt-authentication)
  - [API Documentation](#api-documentation)
- [Password Reset Flow](#password-reset-flow)
- [AWS S3 Storage](#aws-s3-storage)
- [Deployment](#deployment)
- [CI/CD Pipeline](#cicd-pipeline)
- [Security Best Practices](#security-best-practices)

---

## Features

- **User Management**: User registration, login/logout, and regex-based password validation.
- **Notes Management**: Create, view, edit, and delete user-specific notes.
- **Media Support**: Image uploads for notes stored securely via AWS S3.
- **Password Reset**: Email-based OTP verification using Gmail SMTP.
- **Database**: PostgreSQL support for persistent data storage.
- **RESTful API**: Django REST Framework (DRF) with JWT authentication, refresh token handling, and token blacklisting/logout.
- **API Documentation**: Interactive Swagger/OpenAPI documentation.
- **Performance & Security (Redis)**: API response caching, rate limiting on sensitive routes, and temporary OTP storage.
- **Containerization**: Dockerized setup with `Docker Compose` managing Django, PostgreSQL, and Redis.
- **Deployment**: Deployed on AWS EC2 using Nginx as a reverse proxy and Gunicorn as the application server; configured for Render.
- **CI/CD**: Automated deployment pipelines using GitHub Actions.

---

## Tech Stack

| Domain | Technology |
| :--- | :--- |
| **Backend** | Python, Django |
| **Frontend** | HTML, CSS, JavaScript |
| **API Framework** | Django REST Framework (DRF) |
| **Authentication** | JWT (JSON Web Tokens) |
| **API Docs** | drf-spectacular / Swagger UI |
| **Database** | PostgreSQL |
| **Cache / Rate Limit** | Redis |
| **Object Storage** | AWS S3 (`django-storages`, `boto3`) |
| **Email Service** | Gmail SMTP |
| **Containerization** | Docker, Docker Compose |
| **Deployment** | AWS EC2 (also Render compatible) |
| **Web / App Server** | Nginx, Gunicorn |
| **CI/CD** | GitHub Actions |

---

## Project Structure

```text
SI_Django_Notes_Task/
├── api/
│   ├── migrations/
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── notes/
│   ├── migrations/
│   ├── templates/
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── manage.py
├── requirements.txt
├── Dockerfile
├── compose.yaml
├── .dockerignore
├── build.sh
└── .gitignore
```

---

## Local Setup with Docker

Docker Compose handles running the Django application, PostgreSQL database, and Redis as separate containerized services.

```text
Browser / Swagger
       ↓
Django + Gunicorn
   ↙          ↘
PostgreSQL    Redis
```

### Steps to Run Locally

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd SI_Django_Notes_Task
   ```

2. **Create Environment File**  
   Create a `.env` file in the project root containing your required environment variables (Django, PostgreSQL, Gmail SMTP, AWS S3, and Redis).  
   > ⚠️ **Important:** Never commit `.env` or sensitive credentials to version control.

3. **Start Docker Services**
   ```bash
   docker compose up -d --build
   ```

4. **Run Migrations & Create Superuser**
   ```bash
   docker compose exec web python manage.py migrate
   docker compose exec web python manage.py createsuperuser
   ```

5. **Access the Application**  
   Open your browser and navigate to `http://localhost:8000/`.

---

## Redis Integration

Redis is used across the application to enhance performance and security:

* **API Caching**: Responses for note endpoints are cached in Redis using user-specific cache keys. Caches are automatically invalidated upon creation, update, or deletion of notes to prevent serving stale data.
* **Rate Limiting**: Password reset requests are limited to **5 requests per 15 minutes per IP address** via Django's cache framework to prevent brute-force attacks. Exceeding this limit returns HTTP `429 Too Many Requests`.
* **OTP Storage**: Password-reset OTPs are stored temporarily in Redis with an explicit **5-minute expiration time**.

---

## REST API Reference

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/register/` | Register a new user | No |
| `POST` | `/api/token/` | Obtain JWT access and refresh tokens | No |
| `POST` | `/api/token/refresh/` | Generate a new access token using refresh token | No |
| `POST` | `/api/token/logout/` | Logout user and blacklist refresh token | JWT |

### Notes Endpoints

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/notes/` | Retrieve logged-in user's notes | JWT |
| `POST` | `/api/notes/` | Create a new note | JWT |
| `GET` | `/api/notes/<id>/` | Retrieve a specific note by ID | JWT |
| `PUT` | `/api/notes/<id>/` | Fully update a specific note | JWT |
| `PATCH` | `/api/notes/<id>/` | Partially update a specific note | JWT |
| `DELETE` | `/api/notes/<id>/` | Delete a specific note | JWT |

### Password Reset Endpoints

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/forgot-password/` | Request a password-reset OTP | No |
| `POST` | `/api/verify-otp/` | Verify the OTP sent to user's email | No |
| `POST` | `/api/reset-password/` | Set a new password after OTP verification | No |

---

### JWT Authentication

Include the access token obtained from `/api/token/` in the `Authorization` header of all protected requests:

```http
Authorization: Bearer <your_access_token>
```

### API Documentation

Interactive Swagger documentation is available at:
* **Swagger UI:** `/api/docs/`
* **OpenAPI Schema:** `/api/schema/`

---

## Password Reset Flow

The password reset pipeline uses a secure OTP mechanism via Gmail SMTP and Redis:

```text
Password reset request
        ↓
OTP generated
        ↓
OTP stored temporarily in Redis (5 min TTL)
        ↓
OTP sent via Gmail SMTP
        ↓
OTP verification
        ↓
Password reset complete
```

---

## AWS S3 Storage

All images uploaded alongside notes are securely transferred and stored in AWS S3 using `django-storages` and `boto3`. Configuration relies on environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_STORAGE_BUCKET_NAME`).

---

## Deployment

The application is deployed on an **AWS EC2** instance using **Docker Compose**, served behind an **Nginx** reverse proxy with **Gunicorn** handling application requests.

```text
Internet
   ↓
Nginx
   ↓
Django + Gunicorn
   ↙              ↘
PostgreSQL      Redis
```

---

## CI/CD Pipeline

Continuous Integration and Continuous Deployment are automated using **GitHub Actions**:

* **CI (`main` branch)**: Triggers Django system checks, automated unit tests, dependency validation, and Docker build tests.
* **CD (`production` branch)**: Connects to the AWS EC2 instance over SSH, pulls the latest commits on the `production` branch, and runs `docker compose up -d --build`.

---

## Security Best Practices

- Ensure `.env` is listed in `.gitignore` and kept out of version control.
- Never expose API keys, database credentials, Gmail passwords, or private SSH keys.
- Enforce `DEBUG=False` in production environments.
- Protect endpoints by validating user ownership of requested notes.
- Avoid using `docker compose down -v` in production to prevent unintended loss of persistent PostgreSQL volumes.
