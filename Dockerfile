FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# OB-07: Database persists via volume mount at /data
RUN mkdir -p /data

ENV DASHBOARD_PORT=5000

EXPOSE ${DASHBOARD_PORT}

CMD sh -c "gunicorn --bind 0.0.0.0:${DASHBOARD_PORT} --workers 2 --threads 4 'app:create_app()'"
