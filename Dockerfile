FROM python:3-slim
WORKDIR /usr/src/app
EXPOSE 8443/tcp
COPY . .
RUN apt-get update && \
apt-get install -y \
gcc \
netcat \
default-libmysqlclient-dev
RUN pip install --no-cache-dir -r requirements.txt && \
python manage.py collectstatic && \
python manage.py makemigrations
CMD ./main.sh
