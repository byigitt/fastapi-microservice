FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Infrastructure dosyalarını kopyalamak için docker-compose.yml'de volume kullanacağız
# COPY ../../infrastructure /app/infrastructure

# Expose port
EXPOSE 8000

# Run the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 