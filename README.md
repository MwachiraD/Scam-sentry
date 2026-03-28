# Scam Sentry

Scam Sentry is a Django web app that lets users report, search, and browse online scams.
It helps the public identify scam numbers, names, and social media accounts.

🚩 Inspiration

This project was inspired by a real-life experience during my job search.

I was contacted by individuals claiming to offer a job opportunity, but they required urgent submission of documents such as HELB clearance, EACC certificate, KRA compliance, and a Certificate of Good Conduct. They created a sense of urgency by stating that the company director needed the documents within hours.

They later suggested a “fast-track” option through a third party for a small fee.

Recognizing the red flags — urgency, unofficial channels, and payment requests — I chose not to proceed.

This experience revealed how convincing and widespread such scams are, especially for job seekers. Scam Sentry was built to help users detect, report, and avoid these fraudulent tactics.

🎯 Goals
Help users identify scam patterns
Provide a platform to report suspicious activity
Raise awareness about modern scam tactics
Build a community-driven scam intelligence system

## Features

- Report scams with name/number, social media handle, description, and evidence
- Search reports by name, number, or handle
- User accounts with email/password or Google OAuth
- Password reset flow with explicit rate limiting
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
CRON_ALLOWED_IPS=
TRUST_X_FORWARDED_FOR=False
```

Note: If you see `decouple.UndefinedValueError: SECRET_KEY not found`, it means the `.env` file is missing or the `SECRET_KEY` value is not set.

4) Run migrations and seed default scam types

```bash
python manage.py migrate
python manage.py seed_scam_types
python manage.py seed_demo_data
```

5) Start the server

```bash
python manage.py runserver
```

Demo accounts created by `seed_demo_data`:

- `demo_admin` / `DemoAdmin123!`
- `miriam` / `ScamSentry123!`
- `daniel` / `ScamSentry123!`
- `aisha` / `ScamSentry123!`

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
- CRON_ALLOWED_IPS
- DATABASE_URL (defaults to local SQLite locally, but is required in production)
- SITE_NAME
- TRUST_X_FORWARDED_FOR (enable only behind a trusted reverse proxy)

## Evidence File Storage

By default, evidence uploads are stored locally under `media/`.
For production, use S3-compatible storage by setting:

- AWS_STORAGE_BUCKET_NAME
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- AWS_S3_REGION_NAME (optional)
- AWS_S3_ENDPOINT_URL (optional, needed for non-AWS S3-compatible providers)
- AWS_S3_CUSTOM_DOMAIN (optional)
- AWS_S3_ADDRESSING_STYLE (optional)
- AWS_QUERYSTRING_AUTH (optional, defaults to `True`)

When these are set, uploads use S3 via `django-storages`.

Why this matters on Vercel:

- Vercel Functions have a read-only filesystem with only temporary writable scratch space.
- Files written locally can disappear after a cold start, scale event, or new deployment.
- Different function instances do not share the same local upload directory.

So "not persistent" means an uploaded evidence file may appear to work briefly, then later vanish or fail to load.

Fastest production-safe path:

- If you want zero extra code changes, use AWS S3.
- If you want a cheaper S3-compatible provider like Cloudflare R2 or Backblaze B2, this repo now supports that too through `AWS_S3_ENDPOINT_URL`.

## Deploying to Vercel

This repo now includes [`vercel.json`](./vercel.json) and [`api/index.py`](./api/index.py) so Django can run on Vercel's Python runtime.

Important production requirements:

- Use a real Postgres database via `DATABASE_URL`. Do not use SQLite on Vercel.
- Use S3-compatible object storage for evidence uploads. Vercel's local filesystem is not persistent.
- Set `SITE_URL` to your production domain, for example `https://your-domain.vercel.app` or your custom domain.
- Set `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` to include your Vercel domain and any custom domain.
- Set `CRON_SECRET` so the weekly digest endpoint can be called safely by Vercel Cron.
- Set `CRON_ALLOWED_IPS` if your scheduler has stable egress IPs and you want an extra allowlist check.
- Leave `TRUST_X_FORWARDED_FOR=False` unless you are sure your deployment is behind a trusted proxy that rewrites that header.

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
- `CRON_ALLOWED_IPS`
- `TRUST_X_FORWARDED_FOR`
- `AWS_STORAGE_BUCKET_NAME`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_S3_REGION_NAME`
- `AWS_S3_ENDPOINT_URL`
- `AWS_S3_CUSTOM_DOMAIN`
- `AWS_S3_ADDRESSING_STYLE`

Build command:

```bash
python manage.py collectstatic --noinput
```

One-time database/setup commands you should run against the production database before going live:

```bash
python manage.py migrate
python manage.py seed_scam_types
```

Do not run `seed_demo_data` in production.

The weekly digest can be triggered through the secured Django endpoint at `/api/cron/weekly-digest/`, which is already registered in `vercel.json`.

The `/api/init/` endpoint is no longer intended for public deployment automation. Run migrations and seed commands from your deployment command or an authenticated admin session instead of exposing setup actions over HTTP.

### AWS S3 setup

Use this if you want the simplest path with the current app.

1. Create an S3 bucket in AWS.
2. Keep the bucket private.
3. Create an IAM user or app-specific access key with access limited to that bucket.
4. Add these Vercel env vars:

```env
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_S3_REGION_NAME=your-bucket-region
AWS_QUERYSTRING_AUTH=True
```

5. Redeploy.
6. Upload a test evidence file and open its URL from a report page.

With `AWS_QUERYSTRING_AUTH=True`, Django will generate signed URLs so files can stay private in the bucket.

### Cloudflare R2 example

If you prefer Cloudflare R2, set:

```env
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_ACCESS_KEY_ID=your-r2-access-key-id
AWS_SECRET_ACCESS_KEY=your-r2-secret-access-key
AWS_S3_REGION_NAME=auto
AWS_S3_ENDPOINT_URL=https://<ACCOUNT_ID>.r2.cloudflarestorage.com
AWS_S3_ADDRESSING_STYLE=virtual
AWS_QUERYSTRING_AUTH=True
```

## Deploying to Render

- Build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
- Start command: `gunicorn newscamsentry.wsgi:application`
- Set environment variables from the list above
- Set `DEBUG=False` for production

## Notes

- The seed command is idempotent and can be run multiple times.
- `seed_demo_data` is also idempotent and refreshes the same demo users and sample reports.
- For Google OAuth, configure the authorized redirect URI in the Google Cloud Console.
- Digest subscriptions and report-follow alerts now use email confirmation before activation.
