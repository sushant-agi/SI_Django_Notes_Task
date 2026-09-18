# Django Notes App

A Django-based note-taking web application with user authentication, CRUD operations, image uploads, password reset using a security question, and password validation using Regular Expressions.

## Features

- User registration and login/logout
- Password validation using Regex
- Create, view, edit, and delete notes
- User-specific notes (users can access only their own notes)
- Image upload for notes
- Images stored using AWS S3
- Password reset using a security question
- PostgreSQL database
- Deployed on AWS EC2 using Nginx and Gunicorn
- Also configured for deployment on Render

## Tech Stack

- **Backend:** Python, Django
- **Frontend:** HTML, CSS, JavaScript
- **Database:** PostgreSQL
- **Storage:** AWS S3
- **Deployment:** AWS EC2
- **Web Server:** Nginx
- **Application Server:** Gunicorn

## Project Structure

```text
SI_Django_Notes_Task/
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── notes/
│   ├── migrations/
│   ├── templates/
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── manage.py
├── requirements.txt
├── build.sh
└── .gitignore
```

## Local Setup

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd SI_Django_Notes_Task
```

### 2. Create and activate a virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your_secret_key
DEBUG=True
DATABASE_URL=your_database_url

AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_STORAGE_BUCKET_NAME=your_bucket_name
AWS_S3_REGION_NAME=ap-south-1
```

Do **not** commit `.env` or any AWS credentials to GitHub.

### 5. Apply migrations

```bash
python manage.py migrate
```

### 6. Run the development server

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

## Deployment

The application is deployed on AWS EC2 using:

```text
Nginx → Gunicorn → Django
```

Gunicorn and Nginx are configured as system services, so the application continues running after the SSH terminal is closed.

For production, `DEBUG` should be set to:

```env
DEBUG=False
```

## Updating the EC2 Deployment

Changes pushed to GitHub are **not automatically deployed** to EC2.

After pushing new changes:

```bash
cd ~/SI_Django_Notes_Task
git pull
sudo systemctl restart notes
```

If dependencies were changed:

```bash
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart notes
```

## Security Notes

- Keep `.env` out of version control.
- Never expose AWS access keys, database credentials, or the EC2 `.pem` key.
- Use `DEBUG=False` in production.
- Restrict access to user-owned notes through authentication and ownership checks.
