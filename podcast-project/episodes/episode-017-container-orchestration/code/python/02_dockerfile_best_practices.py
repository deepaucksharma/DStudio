#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Docker Best Practices for Indian Companies
Episode 17: Container Orchestration

यह example दिखाता है कि कैसे Zomato, BigBasket जैसी companies
production-grade Dockerfiles बनाती हैं।

Focus: Security, Performance, Size Optimization
"""

import os
import json
import subprocess
import hashlib
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import tempfile

@dataclass
class DockerImageConfig:
    """Docker image configuration with Indian company context"""
    app_name: str
    version: str
    base_image: str
    company: str
    environment: str  # dev, staging, prod
    region: str  # mumbai, bangalore, delhi
    
class ZomatoDockerfileGenerator:
    """
    Zomato-style Dockerfile generator
    Production-ready containers with best practices
    """
    
    def __init__(self):
        self.security_practices = {
            "non_root_user": True,
            "minimal_base_image": True,
            "secret_scanning": True,
            "vulnerability_scanning": True
        }
        
        # Indian company specific configurations
        self.indian_timezones = {
            "mumbai": "Asia/Kolkata",
            "bangalore": "Asia/Kolkata", 
            "delhi": "Asia/Kolkata"
        }
        
        print("🇮🇳 Zomato Dockerfile Generator initialized!")
        print("Production-ready containers banane ke liye ready!")
    
    def generate_multi_stage_dockerfile(self, config: DockerImageConfig) -> str:
        """
        Multi-stage Dockerfile generation - Size optimization के लिए
        Zomato style: Build stage + Runtime stage
        """
        
        dockerfile_content = f"""# Multi-stage Dockerfile for {config.company} - {config.app_name}
# Episode 17: Container Orchestration Best Practices
# Author: Hindi Tech Podcast Team

# Stage 1: Build stage (Build dependencies यहाँ install होंगे)
FROM {config.base_image} AS builder

# Label metadata - Indian company context
LABEL maintainer="{config.company}-devops@company.com"
LABEL company="{config.company}"
LABEL app="{config.app_name}"
LABEL version="{config.version}"
LABEL region="{config.region}"
LABEL environment="{config.environment}"

# Set timezone for Indian operations
ENV TZ={self.indian_timezones.get(config.region, "Asia/Kolkata")}
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Python environment setup
ENV PYTHONUNBUFFERED=1 \\
    PYTHONDONTWRITEBYTECODE=1 \\
    PIP_NO_CACHE_DIR=1 \\
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies (minimal set)
RUN apt-get update && apt-get install -y --no-install-recommends \\
    build-essential \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security (यहाँ security best practice!)
RUN groupadd -r {config.app_name} && useradd -r -g {config.app_name} {config.app_name}

# Set working directory
WORKDIR /app

# Copy requirements first (Docker layer caching के लिए)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Build application (if needed - like static assets, etc.)
RUN python setup.py build 2>/dev/null || echo "No setup.py found"

# Stage 2: Runtime stage (Production image - minimal size)
FROM {config.base_image}-slim AS runtime

# Copy timezone setting
ENV TZ={self.indian_timezones.get(config.region, "Asia/Kolkata")}
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Python environment setup
ENV PYTHONUNBUFFERED=1 \\
    PYTHONDONTWRITEBYTECODE=1 \\
    PATH="/home/{config.app_name}/.local/bin:$PATH"

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    curl \\
    ca-certificates \\
    && rm -rf /var/lib/apt/lists/*

# Create non-root user (security best practice)
RUN groupadd -r {config.app_name} && useradd -r -g {config.app_name} -m {config.app_name}

# Set working directory
WORKDIR /app

# Copy built application from builder stage
COPY --from=builder --chown={config.app_name}:{config.app_name} /app .

# Switch to non-root user (महत्वपूर्ण security practice!)
USER {config.app_name}

# Health check configuration (Kubernetes के लिए जरूरी)
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port (documentation के लिए - actual port exposure run time पर होती है)
EXPOSE 8000

# Default command (production-ready)
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Indian company specific environment variables
ENV COMPANY="{config.company}" \\
    REGION="{config.region}" \\
    APP_ENV="{config.environment}"

# Security: Drop capabilities and set resource limits
# (Kubernetes में actual limits set होंगे)
"""
        
        return dockerfile_content
    
    def generate_dockerignore(self) -> str:
        """
        .dockerignore file generation - Build context optimization
        """
        dockerignore_content = """# .dockerignore for Indian company containers
# Build context optimization के लिए

# Git files
.git
.gitignore
.gitattributes

# Python cache files
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.env
.venv

# Virtual environments
venv/
ENV/
env/
.venv/

# IDE files
.vscode/
.idea/
*.swp
*.swo
*~

# OS files
.DS_Store
Thumbs.db

# Documentation
README.md
docs/
*.md

# Test files
tests/
test_*
*_test.py
pytest.ini
.pytest_cache/

# CI/CD files
.github/
.gitlab-ci.yml
Jenkinsfile
.travis.yml

# Docker files (avoid recursion)
Dockerfile*
docker-compose*.yml
.dockerignore

# Logs
logs/
*.log

# Temporary files
tmp/
temp/
.tmp/

# Node modules (if any)
node_modules/
npm-debug.log*

# Indian company specific
.env.local
.env.development
.env.staging
.env.production
config/secrets/
credentials/

# Large files that shouldn't be in container
*.zip
*.tar.gz
*.rar
dumps/
backups/
"""
        return dockerignore_content
    
    def generate_docker_compose(self, config: DockerImageConfig) -> str:
        """
        Docker Compose for local development
        Indian company context with realistic services
        """
        
        compose_content = f"""version: '3.8'

# Docker Compose for {config.company} - {config.app_name}
# Local development environment

services:
  # Main application service
  {config.app_name}:
    build:
      context: .
      dockerfile: Dockerfile
      target: runtime
    container_name: {config.company}_{config.app_name}
    ports:
      - "8000:8000"
    environment:
      - APP_ENV=development
      - COMPANY={config.company}
      - REGION={config.region}
      - DATABASE_URL=postgresql://zomato_user:password@postgres:5432/zomato_db
      - REDIS_URL=redis://redis:6379/0
      - LOG_LEVEL=DEBUG
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    depends_on:
      - postgres
      - redis
      - monitoring
    networks:
      - {config.company}_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # PostgreSQL database (Indian companies mostly use this)
  postgres:
    image: postgres:15-alpine
    container_name: {config.company}_postgres
    environment:
      - POSTGRES_DB=zomato_db
      - POSTGRES_USER=zomato_user
      - POSTGRES_PASSWORD=password
      - POSTGRES_TIMEZONE=Asia/Kolkata
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
    networks:
      - {config.company}_network
    restart: unless-stopped

  # Redis for caching (Mumbai traffic जैसी speed चाहिए!)
  redis:
    image: redis:7-alpine
    container_name: {config.company}_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - {config.company}_network
    restart: unless-stopped
    command: redis-server --appendonly yes

  # Monitoring stack (Production-ready observability)
  monitoring:
    image: prom/prometheus:latest
    container_name: {config.company}_prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    networks:
      - {config.company}_network
    restart: unless-stopped

  # Grafana for dashboards (देसी metrics visualization)
  grafana:
    image: grafana/grafana:latest
    container_name: {config.company}_grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
      - GF_TIMEZONE=Asia/Kolkata
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana:/etc/grafana/provisioning
    networks:
      - {config.company}_network
    restart: unless-stopped

  # Nginx as reverse proxy (Load balancing के लिए)
  nginx:
    image: nginx:alpine
    container_name: {config.company}_nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - {config.app_name}
    networks:
      - {config.company}_network
    restart: unless-stopped

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  prometheus_data:
    driver: local
  grafana_data:
    driver: local

networks:
  {config.company}_network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

# Production deployment के लिए commands:
# docker-compose up -d
# docker-compose logs -f {config.app_name}
# docker-compose exec {config.app_name} bash
"""
        
        return compose_content
    
    def create_production_files(self, config: DockerImageConfig, output_dir: str):
        """
        Complete production-ready Docker setup creation
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate Dockerfile
        dockerfile_content = self.generate_multi_stage_dockerfile(config)
        with open(os.path.join(output_dir, "Dockerfile"), "w") as f:
            f.write(dockerfile_content)
        
        # Generate .dockerignore
        dockerignore_content = self.generate_dockerignore()
        with open(os.path.join(output_dir, ".dockerignore"), "w") as f:
            f.write(dockerignore_content)
        
        # Generate docker-compose.yml
        compose_content = self.generate_docker_compose(config)
        with open(os.path.join(output_dir, "docker-compose.yml"), "w") as f:
            f.write(compose_content)
        
        # Generate build script
        build_script = self.generate_build_script(config)
        with open(os.path.join(output_dir, "build.sh"), "w") as f:
            f.write(build_script)
        os.chmod(os.path.join(output_dir, "build.sh"), 0o755)
        
        print(f"✅ Production Docker files created in {output_dir}")
        print("🚀 Ready for Mumbai deployment!")
    
    def generate_build_script(self, config: DockerImageConfig) -> str:
        """Build script with Indian company practices"""
        
        script_content = f"""#!/bin/bash
# Build script for {config.company} - {config.app_name}
# Production-ready container building

set -e  # Exit on any error

# Colors for output (Terminal में अच्छा लगता है!)
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

echo -e "${{GREEN}}🇮🇳 Building {config.company} {config.app_name} container...${{NC}}"

# Configuration
IMAGE_NAME="{config.company}/{config.app_name}"
VERSION="{config.version}"
ENVIRONMENT="{config.environment}"
REGION="{config.region}"

# Build timestamp (Indian timezone)
BUILD_TIME=$(TZ=Asia/Kolkata date '+%Y-%m-%d_%H-%M-%S')

echo -e "${{YELLOW}}📦 Building Docker image...${{NC}}"

# Build with build args
docker build \\
  --build-arg BUILD_TIME="$BUILD_TIME" \\
  --build-arg COMPANY="{config.company}" \\
  --build-arg VERSION="$VERSION" \\
  --build-arg ENVIRONMENT="$ENVIRONMENT" \\
  --build-arg REGION="$REGION" \\
  -t $IMAGE_NAME:$VERSION \\
  -t $IMAGE_NAME:latest \\
  -t $IMAGE_NAME:$ENVIRONMENT \\
  .

echo -e "${{GREEN}}✅ Build completed successfully!${{NC}}"

# Image size check (Optimization के लिए important!)
echo -e "${{YELLOW}}📊 Image size analysis:${{NC}}"
docker images $IMAGE_NAME:$VERSION

# Security scan (Production के लिए जरूरी!)
echo -e "${{YELLOW}}🔒 Running security scan...${{NC}}"
if command -v trivy &> /dev/null; then
    trivy image $IMAGE_NAME:$VERSION
else
    echo -e "${{RED}}⚠️  Trivy not installed. Install for security scanning.${{NC}}"
fi

# Test run (Quick sanity check)
echo -e "${{YELLOW}}🧪 Testing container...${{NC}}"
CONTAINER_ID=$(docker run -d -p 8000:8000 $IMAGE_NAME:$VERSION)
sleep 5

# Health check
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${{GREEN}}✅ Health check passed!${{NC}}"
else
    echo -e "${{RED}}❌ Health check failed!${{NC}}"
fi

# Cleanup test container
docker stop $CONTAINER_ID > /dev/null
docker rm $CONTAINER_ID > /dev/null

echo -e "${{GREEN}}🚀 Container ready for deployment!${{NC}}"
echo -e "${{GREEN}}Run: docker run -p 8000:8000 $IMAGE_NAME:$VERSION${{NC}}"

# Registry push instructions
echo -e "${{YELLOW}}📤 To push to registry:${{NC}}"
echo "docker push $IMAGE_NAME:$VERSION"
echo "docker push $IMAGE_NAME:latest"
"""
        
        return script_content

def main():
    """Demonstration of Docker best practices for Indian companies"""
    
    # Zomato example configuration
    zomato_config = DockerImageConfig(
        app_name="order-service",
        version="v1.2.3",
        base_image="python:3.11",
        company="zomato",
        environment="production",
        region="mumbai"
    )
    
    # BigBasket example configuration  
    bigbasket_config = DockerImageConfig(
        app_name="inventory-service",
        version="v2.1.0",
        base_image="python:3.11",
        company="bigbasket",
        environment="staging",
        region="bangalore"
    )
    
    # Ola example configuration
    ola_config = DockerImageConfig(
        app_name="ride-matching",
        version="v3.0.1",
        base_image="python:3.11",
        company="ola",
        environment="production",
        region="delhi"
    )
    
    generator = ZomatoDockerfileGenerator()
    
    # Create production files for all companies
    companies = [
        ("zomato", zomato_config),
        ("bigbasket", bigbasket_config), 
        ("ola", ola_config)
    ]
    
    for company_name, config in companies:
        output_dir = f"/tmp/{company_name}_docker_example"
        generator.create_production_files(config, output_dir)
        print(f"📂 {company_name} files created in: {output_dir}")
    
    print("\\n🎉 All Docker best practices examples created!")
    print("Ready for Indian production deployment! 🇮🇳")

if __name__ == "__main__":
    main()

# Usage examples:
"""
# Generate Zomato-style Docker setup:
python 02_dockerfile_best_practices.py

# Build with security scanning:
./build.sh

# Multi-architecture build (for ARM और x86):
docker buildx build --platform linux/amd64,linux/arm64 -t zomato/order-service:v1.2.3 .

# Production deployment:
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Mumbai datacenter deployment:
docker service create --name zomato-order --replicas 3 zomato/order-service:v1.2.3
"""