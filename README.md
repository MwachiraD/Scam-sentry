# Scam Sentry

Scam Sentry is a Django web app that lets users report, search, and browse online scams.
It helps the public identify scam numbers, names, and social media accounts.

## Features

- Report scams with name/number, social media handle, description, and evidence
- Search reports by name, number, or handle
- User accounts with email/password or Google OAuth
- Personal dashboard to view and edit reports
- Mark reports as resolved
- Public report list with status filters
- Feedback form

## Tech Stack

- Django 5
- Django Allauth (email/password and Google OAuth)
- Bootstrap 5

## Local Setup

1) Create and activate a virtual environment
2) Install dependencies

```bash
pip install -r requirements.txt
```

3) Create a `.env` file (example values)

```env
SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password
```

4) Run migrations and seed default scam types

```bash
python manage.py migrate
python manage.py seed_scam_types
```

5) Start the server

```bash
python manage.py runserver
```

## Environment Variables

Required:
- SECRET_KEY
- DEBUG
- ALLOWED_HOSTS
- GOOGLE_CLIENT_ID
- GOOGLE_CLIENT_SECRET
- EMAIL_HOST_USER
- EMAIL_HOST_PASSWORD

Optional:
- DATABASE_URL (defaults to local SQLite if not set)

## Evidence File Storage

By default, evidence uploads are stored locally under `media/`.
For production, use S3-compatible storage by setting:

- AWS_STORAGE_BUCKET_NAME
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- AWS_S3_REGION_NAME (optional)

When these are set, uploads use S3 via `django-storages`.

## Deploying to Render

- Build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
- Start command: `gunicorn newscamsentry.wsgi:application`
- Set environment variables from the list above
- Set `DEBUG=False` for production

## Notes

- The seed command is idempotent and can be run multiple times.
- For Google OAuth, configure the authorized redirect URI in the Google Cloud Console.
