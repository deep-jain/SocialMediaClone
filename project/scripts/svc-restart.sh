#!/bin/bash

# Stop current services
sudo service nginx stop
sudo service gunicorn stop

# Enter venv
source /home/project/projectenv/bin/activate
python /home/project/manage.py migrate
python /home/project/manage.py collectstatic

# Restart services
sudo service gunicorn start
sudo service nginx restart

