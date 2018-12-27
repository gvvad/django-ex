FROM python:3-slim
WORKDIR /usr/src/app
EXPOSE 8080
COPY . .
RUN apt-get update && \
apt-get install -y \
gcc \
default-libmysqlclient-dev
RUN pip install --no-cache-dir -r requirements.txt && \
python manage.py makemigrations
CMD sh ./main.sh
