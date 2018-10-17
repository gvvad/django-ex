#!/usr/bin/env bash
python ./manage.py kinotbot_schedule &
python ./manage.py rustbot_schedule &
python ./manage.py tolokatbot_schedule &