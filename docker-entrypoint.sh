#!/bin/bash


# Create database migration files
echo "Create database migration files"
python manage.py makemigrations
python manage.py makemigrations application

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate
python manage.py migrate application

#Collect static resources
echo "Collecting static assets"
mkdir static
python manage.py collectstatic --noinput

echo "from django.contrib.auth.models import User; User.objects.filter(username='root').delete(); User.objects.create_superuser('root', 'root@admin.com', 'default-password')" | python manage.py shell

# Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:8000
