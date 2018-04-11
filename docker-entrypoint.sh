#!/bin/sh

# Create database migration files
echo "Create database migration files"
python manage.py makemigrations
python manage.py makemigrations arc_application

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate --settings=$PROJECT_SETTINGS
python manage.py migrate arc_application --settings=$PROJECT_SETTINGS

#Collect static resources
echo "Collecting static assets"
mkdir -p static
python manage.py collectstatic --noinput --settings=$PROJECT_SETTINGS

python manage.py loaddata initial_root_user --settings=$PROJECT_SETTINGS
python manage.py loaddata initial_arc_user --settings=$PROJECT_SETTINGS

# Start server
echo "Starting server"
python manage.py runserver --settings=$PROJECT_SETTINGS 0.0.0.0:8000
