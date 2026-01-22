# Base image: Python 3.11 Slim (Debian-based)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (needed for lxml sometimes)
RUN apt-get update && apt-get install -y \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for shared data mapping
RUN mkdir -p ../dat/json ../dat/processed

# Define entrypoint
CMD ["python", "data_converter.py"]
