#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Convert static asset files
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py migrate

# Fetch initial news if database is empty/needs update
echo "Running background fetcher..."
python manage.py fetch_news
