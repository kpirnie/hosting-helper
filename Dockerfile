# Multi-stage Dockerfile for KP Hosting Helper

# Stage 1: Base dependencies
FROM docker.io/library/python:3-alpine as base

# runtime dependencies
RUN apk add --no-cache \
    curl \
    restic \
    optipng \
    jpegoptim \
    gifsicle \
    libwebp-tools \
    mariadb-client \
    inotify-tools \
    bash \
    tar \
    perl \
    && mkdir -p /usr/local/sbin /etc/init.d

# Stage 2: Python dependencies
FROM docker.io/library/python:3-alpine as python-deps

# Install build dependencies only in this stage
RUN apk add --no-cache \
    gcc \
    musl-dev \
    python3-dev \
    mariadb-dev \
    mariadb-connector-c-dev

WORKDIR /build

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 3: Application
FROM base as app

# Copy Python packages from builder
COPY --from=python-deps /root/.local /root/.local

# Set PATH to include user-installed packages
ENV PATH=/root/.local/bin:$PATH

# Create app directory
WORKDIR /app

# Copy application source
COPY source/ /app/

# Install WP-CLI
RUN curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar && \
    chmod +x wp-cli.phar && \
    mv wp-cli.phar /usr/local/bin/wp

# Install maldet (required)
RUN mkdir -p /usr/local/src && \
    curl -L http://www.rfxn.com/downloads/maldetect-current.tar.gz -o /tmp/maldetect.tar.gz && \
    tar -xzf /tmp/maldetect.tar.gz -C /usr/local/src/ && \
    cd /usr/local/src/maldetect-* && \
    bash install.sh && \
    cd / && \
    rm -rf /tmp/maldetect.tar.gz /usr/local/src/maldetect-*

# Create necessary directories
RUN mkdir -p /tmp/restore /tmp/backup-mount

# Environment variables with defaults (can be overridden)
ENV RESTIC_PASSWORD="" \
    KP_S3_KEY="" \
    KP_S3_SECRET="" \
    KP_S3_ENDPOINT="s3.amazonaws.com" \
    KP_S3_BUCKET="" \
    KP_S3_REGION="us-east-1" \
    KP_RETENTION_DAYS="30" \
    KP_BACKUP_NAME="" \
    KP_PATH_START="/home/" \
    KP_PATH_FOR_APPS="webapps" \
    KP_MYSQL_HOST="localhost" \
    KP_MYSQL_DEFAULTS="" \
    KP_MYSQL_USER="" \
    KP_MYSQL_PASSWORD="" \
    PYTHONUNBUFFERED=1

# Create entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["--help"]