#!/bin/bash

# Stop current services
sudo service nginx stop
sudo service gunicorn stop

# Enter venv
source /home/myprojectdir/myprojectenv/bin/activate
python /home/myprojectdir/manage.py makemigrations myproject
python /home/myprojectdir/manage.py migrate
python /home/myprojectdir/manage.py collectstatic

# Restart services
sudo service gunicorn start
sudo service nginx restart

