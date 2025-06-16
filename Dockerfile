FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install supernote flask

WORKDIR /app

# Copy application files
COPY . .

EXPOSE 8000

CMD ["python", "app.py"]
