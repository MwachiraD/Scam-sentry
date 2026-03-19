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
CSRF_TRUSTED_ORIGINS=
DATABASE_URL=
SITE_URL=http://127.0.0.1:8000
SITE_NAME=Scam Sentry
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password
CRON_SECRET=change-me
```

Note: If you see `decouple.UndefinedValueError: SECRET_KEY not found`, it means the `.env` file is missing or the `SECRET_KEY` value is not set.

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
- SITE_URL
- GOOGLE_CLIENT_ID
- GOOGLE_CLIENT_SECRET
- EMAIL_HOST_USER
- EMAIL_HOST_PASSWORD

Optional:
- CSRF_TRUSTED_ORIGINS
- CRON_SECRET
- DATABASE_URL (defaults to local SQLite locally, but is required in production)
- SITE_NAME

## Evidence File Storage

By default, evidence uploads are stored locally under `media/`.
For production, use S3-compatible storage by setting:

- AWS_STORAGE_BUCKET_NAME
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- AWS_S3_REGION_NAME (optional)

When these are set, uploads use S3 via `django-storages`.

## Deploying to Vercel

This repo now includes [`vercel.json`](./vercel.json) and [`api/index.py`](./api/index.py) so Django can run on Vercel's Python runtime.

Important production requirements:

- Use a real Postgres database via `DATABASE_URL`. Do not use SQLite on Vercel.
- Use S3-compatible object storage for evidence uploads. Vercel's local filesystem is not persistent.
- Set `SITE_URL` to your production domain, for example `https://your-domain.vercel.app` or your custom domain.
- Set `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` to include your Vercel domain and any custom domain.
- Set `CRON_SECRET` so the weekly digest endpoint can be called safely by Vercel Cron.

Suggested Vercel environment variables:

- `SECRET_KEY`
- `DEBUG=False`
- `DATABASE_URL`
- `ALLOWED_HOSTS=.vercel.app,your-domain.com`
- `CSRF_TRUSTED_ORIGINS=https://*.vercel.app,https://your-domain.com`
- `SITE_URL=https://your-domain.com`
- `SITE_NAME=Scam Sentry`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `CRON_SECRET`
- `AWS_STORAGE_BUCKET_NAME`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_S3_REGION_NAME`

Build command:

```bash
python manage.py collectstatic --noinput
```

One-time database/setup commands you should run against the production database before going live:

```bash
python manage.py migrate
python manage.py seed_scam_types
```

The weekly digest can be triggered through the secured Django endpoint at `/api/cron/weekly-digest/`, which is already registered in `vercel.json`.

## Deploying to Render

- Build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
- Start command: `gunicorn newscamsentry.wsgi:application`
- Set environment variables from the list above
- Set `DEBUG=False` for production

## Notes

- The seed command is idempotent and can be run multiple times.
- For Google OAuth, configure the authorized redirect URI in the Google Cloud Console.
