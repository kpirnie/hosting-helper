FROM docker.io/library/debian:12-slim

RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    python3 \
    python3-pip \
    python3-mysql \
    mariadb-client \
    restic \
    optipng \
    jpegoptim \
    gifsicle \
    webp \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY release/kp-portable /usr/local/bin/kp
RUN chmod +x /usr/local/bin/kp

ENTRYPOINT ["/usr/local/bin/kp"]