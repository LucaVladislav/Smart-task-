FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiem codul backend
COPY app ./app

# Copiem front-end-ul (index.html)
COPY frontend ./frontend

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
