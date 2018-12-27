#!/bin/bash
python ./manage.py makemigrations
python ./manage.py migrate
gunicorn --bind 0.0.0.0:8080 -w 2 wsgi
#python ./manage.py kinotbot_schedule &
#python ./manage.py rustbot_schedule &
#python ./manage.py tolokatbot_schedule &
