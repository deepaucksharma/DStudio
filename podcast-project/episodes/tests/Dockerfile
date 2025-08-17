# Dockerfile for Hindi Podcast Testing Framework
# हिंदी पॉडकास्ट टेस्टिंग फ्रेमवर्क के लिए Docker

FROM python:3.11-slim

LABEL maintainer="Agent 6 - Testing Framework Team"
LABEL description="Comprehensive testing framework for Hindi Podcast Episodes 92-100"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    pkg-config \
    libpq-dev \
    netcat-openbsd \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for k6 load testing
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Install k6 for load testing
RUN wget https://github.com/grafana/k6/releases/download/v0.47.0/k6-v0.47.0-linux-amd64.tar.gz \
    && tar -xzf k6-v0.47.0-linux-amd64.tar.gz \
    && mv k6-v0.47.0-linux-amd64/k6 /usr/local/bin/ \
    && rm -rf k6-v0.47.0-linux-amd64*

# Install Go for Go unit tests
RUN wget https://golang.org/dl/go1.19.linux-amd64.tar.gz \
    && tar -C /usr/local -xzf go1.19.linux-amd64.tar.gz \
    && rm go1.19.linux-amd64.tar.gz
ENV PATH=$PATH:/usr/local/go/bin

# Install Java for Java unit tests
RUN apt-get update && apt-get install -y openjdk-11-jdk maven \
    && rm -rf /var/lib/apt/lists/*
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

# Create app directory
WORKDIR /app

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash testuser
RUN chown -R testuser:testuser /app

# Copy requirements first for better caching
COPY requirements.txt .
COPY requirements-dev.txt* ./

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && if [ -f requirements-dev.txt ]; then pip install -r requirements-dev.txt; fi

# Copy application code
COPY . .

# Fix permissions
RUN chown -R testuser:testuser /app

# Switch to non-root user
USER testuser

# Create directories for test outputs
RUN mkdir -p /app/test-results \
    && mkdir -p /app/logs \
    && mkdir -p /app/reports \
    && mkdir -p /app/coverage

# Environment variables for testing
ENV PYTHONPATH=/app
ENV TEST_ENV=docker
ENV INDIAN_REGION=mumbai

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import pytest; print('Testing framework ready')" || exit 1

# Default command
CMD ["make", "help"]

# Build arguments for customization
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION

# Labels for metadata
LABEL org.label-schema.build-date=$BUILD_DATE
LABEL org.label-schema.vcs-ref=$VCS_REF
LABEL org.label-schema.version=$VERSION
LABEL org.label-schema.schema-version="1.0"

# Expose ports for test services
EXPOSE 8080 8500 6379 5432

# Volume mounts for test data and reports
VOLUME ["/app/test-results", "/app/logs", "/app/reports", "/app/coverage"]

# Entry point script for initialization
COPY docker-entrypoint.sh /usr/local/bin/
ENTRYPOINT ["docker-entrypoint.sh"]