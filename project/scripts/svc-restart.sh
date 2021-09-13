#!/bin/bash/

# Stop current services
sudo service nginx stop
sudo service gunicorn stop

# Enter venv
source ../projectenv/bin/activate
python ../manage.py migrate
python ../manage.py collectstatic

# Restart services
sudo service gunicorn start
sudo service nginx restart

