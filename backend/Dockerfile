FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y 
    build-essential 
    libpq-dev 
    wget 
    procps 
    && rm -rf /var/lib/apt/lists/*

# For now, just create a dummy requirements.txt if it doesn't exist
RUN touch requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Dummy app structure
RUN mkdir -p app/tasks
RUN touch app/__init__.py app/main.py app/tasks/celery_app.py

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
