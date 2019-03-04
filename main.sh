#!/bin/bash

PORT="8443"

db_wait() {
while ! nc -z "$POSTGRESQL_SERVICE_HOST" "$POSTGRESQL_SERVICE_PORT"; do
sleep 1
done
}

db_init_superuser() {
python ./manage.py init_superuser
}

db_migrate() {
python ./manage.py migrate
}

start_gunicorn() {
if [[ -f "$KEYFILE" ]]; then
gunicorn --bind 0.0.0.0:"$PORT" -w 2 --keyfile "$KEYFILE" --certfile "$CERTFILE" wsgi
else
gunicorn --bind 0.0.0.0:"$PORT" -w 2 wsgi
fi
}

set_webhooks() {
python ./manage.py tolokatbot_setwebhook
python ./manage.py kinotbot_setwebhook
python ./manage.py rustbot_setwebhook
}

start_schedule() {
python ./manage.py tolokatbot_schedule &
python ./manage.py kinotbot_schedule &
python ./manage.py rustbot_schedule &
}

run_sequence() {
db_wait
db_migrate
db_init_superuser
set_webhooks
start_schedule
start_gunicorn
}

if [[ "$1" = "migrate" ]]; then
    db_migrate
fi

if [[ "$1" = "schedule" ]]; then
    start_schedule
fi

if [[ "$1" = "sequence" ]]; then
    run_sequence
fi

#Default entry point
if [[ "$1" = "" ]]; then
    run_sequence
fi
