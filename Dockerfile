# Base image with Python 3.11 (slim to keep image small)
FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install dependencies first to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Ensure runtime folders exist (also created in config, but kept for clarity)
RUN mkdir -p logs data backup media

# Run the bot
CMD ["python", "main.py"]
