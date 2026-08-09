# Production Dockerfile for Banking Transaction System
# Engineer: Shaik Ahamed Eshak Nowfal

# Use slim Python image — ~130MB vs 645MB for ubuntu
FROM python:3.12-slim

# Metadata
LABEL maintainer="Shaik Ahamed Eshak Nowfal"
LABEL application="banking-transaction-system"
LABEL version="1.0"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

# Create non-root user for security (never run as root in production)
RUN groupadd -r bankingapp && useradd -r -g bankingapp bankingapp

# Set working directory
WORKDIR /app

# Install system dependencies (mysql client for pymysql)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        default-libmysqlclient-dev \
        pkg-config \
        curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Change ownership to non-root user
RUN chown -R bankingapp:bankingapp /app

# Switch to non-root user
USER bankingapp

# Document exposed port
EXPOSE 5000

# Health check — Docker monitors container health
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Production command: gunicorn with 2 workers
CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:5000", \
     "--timeout", "30", "--log-level", "info", "app:app"]
