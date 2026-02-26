# KP Hosting Helper <a name="top"></a>

[![Build and Push Docker Image](https://github.com/kpirnie/hosting-helper/actions/workflows/docker-build.yml/badge.svg)](https://github.com/kpirnie/hosting-helper/actions/workflows/docker-build.yml)
[![License: MIT](https://img.shields.io/github/license/kpirnie/hosting-helper)](https://github.com/kpirnie/hosting-helper/blob/main/LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/kpirnie/hosting-helper)](https://github.com/kpirnie/hosting-helper/commits/main)
[![GitHub Issues](https://img.shields.io/github/issues/kpirnie/hosting-helper)](https://github.com/kpirnie/hosting-helper/issues)
[![Image Size](https://ghcr-badge.egpl.dev/kpirnie/wmh-helper/size?tag=latest&label=image%20size)](https://github.com/kpirnie/hosting-helper/pkgs/container/wmh-helper)
[![Kevin Pirnie](https://img.shields.io/badge/Kevin%20Pirnie-.com-blue)](https://kevinpirnie.com/)

[Requirements](#requirements) | [Quick Start](#quick-start) | [Configuration](#configuration) | [Commands](#commands) | [Usage](#usage)

A containerized Python 3 application for managing web server backup, restore, optimization, and security operations. This is a Docker-only application — all operations run inside the container.

---

## Requirements <a name="requirements"></a>

[Requirements](#requirements) | [Quick Start](#quick-start) | [Configuration](#configuration) | [Commands](#commands) | [Usage](#usage)

- Docker or Podman
- Docker Compose or Podman Compose

[Back To Top](#top)

---

## Quick Start <a name="quick-start"></a>

[Requirements](#requirements) | [Quick Start](#quick-start) | [Configuration](#configuration) | [Commands](#commands) | [Usage](#usage)

```bash
# Pull the latest image
docker pull ghcr.io/kpirnie/wmh-helper:latest

# Create your environment file
cat > .env << EOF
KP_S3_KEY=your_s3_key
KP_S3_SECRET=your_s3_secret
KP_S3_BUCKET=your_bucket_name
RESTIC_PASSWORD=your_encryption_password
EOF

# Run a backup
docker run --rm \
  --env-file .env \
  -v /home:/home:ro \
  --network host \
  ghcr.io/kpirnie/wmh-helper:latest backup --backup all
```

[Back To Top](#top)

---

## Configuration <a name="configuration"></a>

[Requirements](#requirements) | [Quick Start](#quick-start) | [Configuration](#configuration) | [Commands](#commands) | [Usage](#usage)

All configuration is handled via environment variables passed to the container. No manual config files are needed.

### Environment Variables

#### S3 Storage (Required for Backup/Restore)

| Variable | Description | Default |
|----------|-------------|---------|
| `KP_S3_KEY` | S3 API Key | |
| `KP_S3_SECRET` | S3 API Secret | |
| `KP_S3_ENDPOINT` | S3 endpoint | `s3.amazonaws.com` |
| `KP_S3_BUCKET` | S3 bucket name | |
| `KP_S3_REGION` | S3 region | `us-east-1` |

#### Backup

| Variable | Description | Default |
|----------|-------------|---------|
| `RESTIC_PASSWORD` | Encryption password (auto-generated if not set) | |
| `KP_RETENTION_DAYS` | Days to retain backups | `30` |
| `KP_BACKUP_NAME` | Name for this backup set | hostname |

#### Paths

| Variable | Description | Default |
|----------|-------------|---------|
| `KP_PATH_START` | Starting path for user homes | `/home/` |
| `KP_PATH_FOR_APPS` | Application directory name | `webapps` |

#### MySQL/MariaDB

| Variable | Description | Default |
|----------|-------------|---------|
| `KP_MYSQL_HOST` | MySQL host | `localhost` |
| `KP_MYSQL_DEFAULTS` | Path to MySQL defaults file | |
| `KP_MYSQL_USER` | MySQL admin username | |
| `KP_MYSQL_PASSWORD` | MySQL admin password | |

### Example .env File

```bash
# S3 Configuration
KP_S3_KEY=AKIAIOSFODNN7EXAMPLE
KP_S3_SECRET=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
KP_S3_ENDPOINT=s3.amazonaws.com
KP_S3_BUCKET=my-backup-bucket
KP_S3_REGION=us-east-1

# Backup Configuration
RESTIC_PASSWORD=my-super-secret-encryption-password
KP_RETENTION_DAYS=30
KP_BACKUP_NAME=webserver-01

# Path Configuration
KP_PATH_START=/home/
KP_PATH_FOR_APPS=webapps

# MySQL Configuration
KP_MYSQL_HOST=localhost
KP_MYSQL_DEFAULTS=/etc/mysql/debian.cnf
```

[Back To Top](#top)

---

## Commands <a name="commands"></a>

[Requirements](#requirements) | [Quick Start](#quick-start) | [Configuration](#configuration) | [Commands](#commands) | [Usage](#usage)

All commands follow this format:

```bash
docker run --rm --env-file .env [volumes] ghcr.io/kpirnie/wmh-helper:latest [command] [arguments]
```

### backup

Backs up accounts, applications, databases, or custom paths to S3-compatible storage.

**Required:** `--backup account|acct|application|app|database|db|other|all`

```bash
# Backup everything
docker run --rm --env-file .env \
  -v /home:/home:ro \
  -v /etc/mysql:/etc/mysql:ro \
  --network host \
  ghcr.io/kpirnie/wmh-helper:latest backup --backup all

# Backup a specific application
docker run --rm --env-file .env \
  -v /home:/home:ro \
  --network host \
  ghcr.io/kpirnie/wmh-helper:latest backup --backup app --account myuser --app mysite

# Backup a specific database
docker run --rm --env-file .env \
  -v /etc/mysql:/etc/mysql:ro \
  --network host \
  ghcr.io/kpirnie/wmh-helper:latest backup --backup db --database mydb

# Backup custom paths
docker run --rm --env-file .env \
  -v /etc:/etc:ro \
  -v /var:/var:ro \
  ghcr.io/kpirnie/wmh-helper:latest backup --backup other --paths /etc/nginx,/var/www
```

### restore

Interactive restore wizard that guides you through restoring from backup.

```bash
docker run --rm -it --env-file .env \
  -v /home:/home \
  -v /tmp/restore:/tmp/restore \
  --network host \
  ghcr.io/kpirnie/wmh-helper:latest restore
```

### mount

Mounts a backup repository to a local directory for browsing. Runs in background by default.

**Optional flags:** `--source`, `--destination`, `--unmount`, `--list`, `--foreground`

```bash
# Interactive mount (menu-driven)
docker run --rm -it --env-file .env \
  -v /tmp/backup-mount:/tmp/backup-mount \
  ghcr.io/kpirnie/wmh-helper:latest mount

# Mount a specific repo directly
docker run --rm --env-file .env \
  -v /tmp/backup-mount:/tmp/backup-mount \
  ghcr.io/kpirnie/wmh-helper:latest mount \
  --source apps/myuser/mysite \
  --destination /tmp/backup-mount

# Unmount
docker run --rm --env-file .env \
  ghcr.io/kpirnie/wmh-helper:latest mount --unmount /tmp/backup-mount

# List active mounts
docker run --rm --env-file .env \
  ghcr.io/kpirnie/wmh-helper:latest mount --list
```

### optimages

Optimizes PNG, JPG, GIF, WebP, and SVG images to reduce file sizes.

**Required:** `--optimize account|acct|application|app|other|all`

```bash
# Optimize all images
docker run --rm --env-file .env \
  -v /home:/home \
  ghcr.io/kpirnie/wmh-helper:latest optimages --optimize all

# Optimize a specific application
docker run --rm --env-file .env \
  -v /home:/home \
  ghcr.io/kpirnie/wmh-helper:latest optimages --optimize app --account myuser --app mysite

# Optimize custom paths
docker run --rm --env-file .env \
  -v /var/www:/var/www \
  ghcr.io/kpirnie/wmh-helper:latest optimages --optimize other --paths /var/www/images
```

### scan

Scans for malware and viruses using maldet.

**Required:** `--scan account|acct|application|app|other|all`

**Optional:** `--auto_quarantine`, `--auto_clean`

```bash
# Scan everything
docker run --rm --env-file .env \
  -v /home:/home:ro \
  ghcr.io/kpirnie/wmh-helper:latest scan --scan all

# Scan and auto-quarantine
docker run --rm --env-file .env \
  -v /home:/home \
  ghcr.io/kpirnie/wmh-helper:latest scan --scan all --auto_quarantine

# Scan a specific application
docker run --rm --env-file .env \
  -v /home:/home:ro \
  ghcr.io/kpirnie/wmh-helper:latest scan --scan app --account myuser --app mysite
```

### freem

Clears system caches and frees unused memory.

```bash
docker run --rm --privileged \
  ghcr.io/kpirnie/wmh-helper:latest freem
```

[Back To Top](#top)

---

## Usage <a name="usage"></a>

[Requirements](#requirements) | [Quick Start](#quick-start) | [Configuration](#configuration) | [Commands](#commands) | [Usage](#usage)

### Docker Compose

```yaml
services:
  kp-helper:
    image: ghcr.io/kpirnie/wmh-helper:latest
    env_file: .env
    volumes:
      - /home:/home:ro
      - /etc/mysql:/etc/mysql:ro
      - kp-restore:/tmp/restore
    network_mode: "host"
    restart: "no"
    command: backup --backup all

volumes:
  kp-restore:
```

```bash
# Run any command via compose
docker compose run --rm kp-helper backup --backup all
docker compose run --rm kp-helper restore
docker compose run --rm kp-helper optimages --optimize all
docker compose run --rm kp-helper scan --scan all
```

### Automated Backups via systemd

**`/etc/systemd/system/kp-backup.service`:**

```ini
[Unit]
Description=KP Hosting Helper Backup
After=network.target docker.service
Requires=docker.service

[Service]
Type=oneshot
ExecStart=/usr/bin/docker run --rm \
  --env-file /opt/kp-helper/.env \
  -v /home:/home:ro \
  -v /etc/mysql:/etc/mysql:ro \
  --network host \
  ghcr.io/kpirnie/wmh-helper:latest backup --backup all
```

**`/etc/systemd/system/kp-backup.timer`:**

```ini
[Unit]
Description=Run KP Backup Daily at 2 AM

[Timer]
OnCalendar=*-*-* 02:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now kp-backup.timer
sudo systemctl status kp-backup.timer
```

### Automated Backups via Cron

```bash
0 2 * * * /usr/bin/docker run --rm \
  --env-file /opt/kp-helper/.env \
  -v /home:/home:ro \
  -v /etc/mysql:/etc/mysql:ro \
  --network host \
  ghcr.io/kpirnie/wmh-helper:latest backup --backup all >> /var/log/kp-backup.log 2>&1
```

### Volume Mount Reference

```bash
# Read-only (backups, scans)
-v /home:/home:ro
-v /etc/mysql:/etc/mysql:ro

# Read-write (image optimization, restore)
-v /home:/home
-v /tmp/restore:/tmp/restore
```

### Network Modes

```bash
# Host networking — required when MySQL is on localhost
--network host

# Bridge networking — use when MySQL is on a remote host
--network bridge -e KP_MYSQL_HOST=mysql.example.com
```

### Security

```bash
# Protect your .env file
chmod 600 .env

# Store it outside web roots
/opt/kp-helper/.env   # correct
/var/www/.env         # wrong
```

### Building from Source

```bash
git clone https://github.com/kpirnie/hosting-helper.git
cd hosting-helper

docker build -t kp-hosting-helper:latest .
# or
podman build -t kp-hosting-helper:latest .
```

Images are automatically built and published to `ghcr.io/kpirnie/wmh-helper` on every push to `main`, tagged as both `:latest` and `:<commit-sha>`.

### Troubleshooting

```bash
# View logs
docker logs kp-hosting-helper

# Drop into the container for debugging
docker run --rm -it --env-file .env \
  -v /home:/home \
  --network host \
  --entrypoint /bin/bash \
  ghcr.io/kpirnie/wmh-helper:latest

# Pull latest image
docker pull ghcr.io/kpirnie/wmh-helper:latest
```

[Back To Top](#top)

---

## License

MIT License — see [LICENSE](LICENSE) for details.

## Support

- GitHub: https://github.com/kpirnie/hosting-helper
- Issues: https://github.com/kpirnie/hosting-helper/issues

[Back To Top](#top)