# Dockerfile

FROM python:3.11-slim

# Environment Variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# System Dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Working Directory
WORKDIR /app

# Copy Requirements
COPY requirements.txt .

# Install Python Dependencies
RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

# Copy Project Files

COPY . .

# Create Required Directories

RUN mkdir -p \
    data/raw \
    data/processed \
    logs \
    models

# Expose Ports

EXPOSE 8080
EXPOSE 8501
EXPOSE 8888

# Default Command

CMD ["bash"]
