# =============================================================
# Stage 1: Builder
# Purpose: compile Python packages that need C extensions
# This stage is DISCARDED after build — never in final image
# =============================================================
FROM python:3.12-slim AS builder

# Install build tools (gcc, headers needed to compile pymysql)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        default-libmysqlclient-dev \
        pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install packages to /install directory
# --prefix=/install = all files go to /install instead of system Python
# This makes it easy to copy JUST the packages to runtime stage
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# =============================================================
# Stage 2: Runtime
# Purpose: minimal production image with only what is needed
# This IS the final image — what gets pushed to ECR
# =============================================================
FROM python:3.12-slim AS runtime

# Metadata
LABEL maintainer="Shaik Ahamed Eshak Nowfal"
LABEL application="banking-transaction-system"
LABEL version="2.0"
LABEL build-type="multi-stage"

# Security: non-root user
RUN groupadd -r bankingapp && useradd -r -g bankingapp bankingapp

# Set environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

# Install ONLY runtime system dependencies
# No gcc here — runtime does not need to compile anything
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        default-libmysqlclient-dev \
        curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy compiled packages from builder stage
# gcc is NOT copied — only the compiled .so files and Python packages
COPY --from=builder /install /usr/local

# Copy application code
COPY app.py .

# Set ownership
RUN chown -R bankingapp:bankingapp /app

# Switch to non-root user
USER bankingapp

# Document port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Production command
CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:5000", \
     "--timeout", "30", "--log-level", "info", "app:app"]
