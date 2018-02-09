#!/bin/bash

echo "from django.contrib.auth.models import User; User.objects.filter(email='admin@admin.com').delete(); User.objects.create_superuser('admin', 'admin@admin.com', 'admin')" | python manage.py shell



# Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:8000