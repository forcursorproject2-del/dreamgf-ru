FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for torch and audio
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data temp characters lora

# Expose port
EXPOSE 10000

# Run the application
CMD ["python", "main.py"]
