FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV PORT=8080
ENV DJANGO_SETTINGS_MODULE=webapp.settings

CMD exec gunicorn --bind :$PORT webapp.wsgi 