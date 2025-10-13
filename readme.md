# KP Hosting Helper App <a name="top"></a>

[Requirements](#requirements) | [Description](#description) | [Quick Start](#quick-start) | [Installation](#installation) | [Configuration](#configuration) | [Commands](#commands) | [Usage](#usage)

A containerized Python 3 application for managing web server backup, restore, optimization, and security operations.

## Requirements <a name="requirements"></a>

[Requirements](#requirements) | [Description](#description) | [Quick Start](#quick-start) | [Installation](#installation) | [Configuration](#configuration) | [Commands](#commands) | [Usage](#usage)

**Container Runtime**
- Docker or Podman
- Docker Compose or Podman Compose

**Or for bare-metal installation:**
- Ubuntu 18.04, 20.04, or 22.04
- Python 3.6+
- CLI and Shell Access

[Back To Top](#top)

## Description <a name="description"></a>

[Requirements](#requirements) | [Description](#description) | [Quick Start](#quick-start) | [Installation](#installation) | [Configuration](#configuration) | [Commands](#commands) | [Usage](#usage)

A containerized application for managing web server operations including:

- **Backup & Restore**: Automated backups to S3-compatible storage with encryption
- **Image Optimization**: Compress JPG, PNG, GIF, WebP, and SVG images
- **Security Scanning**: Malware and virus scanning with maldet
- **WordPress Management**: Automated WordPress core and plugin updates with rollback
- **System Utilities**: Memory optimization and cache management

All operations are fully containerized and configured via environment variables.

[Back To Top](#top)

## Quick Start <a name="quick-start"></a>

[Requirements](#requirements) | [Description](#description) | [Quick Start](#quick-start) | [Installation](#installation) | [Configuration](#configuration) | [Commands](#commands) | [Usage](#usage)

### Using Pre-built Image from GitHub Container Registry

```bash
# Pull the latest image
docker pull ghcr.io/kpirnie/wmh-helper:latest

# Or with Podman
podman pull ghcr.io/kpirnie/wmh-helper:latest

# Create .env file
cat > .env << EOF
S3_KEY=your_s3_key
S3_SECRET=your_s3_secret
S3_BUCKET=your_bucket_name
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

## Installation <a name="installation"></a>

[Requirements](#requirements) | [Description](#description) | [Quick Start](#quick-start) | [Installation](#installation) | [Configuration](#configuration) | [Commands](#commands) | [Usage](#usage)

### Option 1: Use Pre-built Image (Recommended)

The easiest way is to use the pre-built image from GitHub Container Registry:

```bash
# Pull the image
docker pull ghcr.io/kpirnie/wmh-helper:latest

# Or with Podman
podman pull ghcr.io/kpirnie/wmh-helper:latest
```

### Option 2: Build from Source

Clone the repository and build locally:

```bash
# Clone the repository
git clone https://github.com/kpirnie/hosting-helper.git
cd hosting-helper

# Build with Docker
docker build -t kp-hosting-helper:latest .

# Or build with Podman
podman build -t kp-hosting-helper:latest .

# Or use docker-compose/podman-compose
docker-compose build
```

### Option 3: Automated Builds

GitHub Actions automatically builds and publishes new images on every push to `main`. Images are tagged as:
- `ghcr.io/kpirnie/wmh-helper:latest` - Latest build
- `ghcr.io/kpirnie/wmh-helper:<commit-sha>` - Specific commit

[Back To Top](#top)

## Configuration <a name="configuration"></a>

[Requirements](#requirements) | [Description](#description) | [Quick Start](#quick-start) | [Installation](#installation) | [Configuration](#configuration) | [Commands](#commands) | [Usage](#usage)

All configuration is done via environment variables. No manual config files needed!

### Create Environment File

```bash
# Copy the example file
cp .env.example .env

# Edit with your settings
nano .env
```

### Environment Variables

#### S3 Storage Configuration (Required for Backup/Restore)

- **`S3_KEY`** - Your S3 API Key
- **`S3_SECRET`** - Your S3 API Secret
- **`S3_ENDPOINT`** - S3 endpoint (default: `s3.amazonaws.com`)
- **`S3_BUCKET`** - S3 bucket name for backups
- **`S3_REGION`** - S3 region (default: `us-east-1`)

#### Backup Configuration

- **`RESTIC_PASSWORD`** - Encryption password for backups (auto-generated if not provided)
- **`RETENTION_DAYS`** - Days to retain backups (default: `30`)
- **`BACKUP_NAME`** - Name for this backup set (default: hostname)

#### Path Configuration

- **`PATH_START`** - Starting path for user homes (default: `/home/`)
- **`PATH_FOR_APPS`** - Application directory name (default: `webapps`)

#### MySQL/MariaDB Configuration

- **`MYSQL_HOST`** - MySQL host (default: `localhost`)
- **`MYSQL_DEFAULTS`** - Path to MySQL defaults file (e.g., `/etc/mysql/debian.cnf`)
- **`MYSQL_USER`** - MySQL admin username (if not using defaults file)
- **`MYSQL_PASSWORD`** - MySQL admin password (if not using defaults file)

#### Example .env File

```bash
# S3 Configuration
S3_KEY=AKIAIOSFODNN7EXAMPLE
S3_SECRET=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
S3_ENDPOINT=s3.amazonaws.com
S3_BUCKET=my-backup-bucket
S3_REGION=us-east-1

# Backup Configuration
RESTIC_PASSWORD=my-super-secret-encryption-password
RETENTION_DAYS=30
BACKUP_NAME=webserver-01

# Path Configuration
PATH_START=/home/
PATH_FOR_APPS=webapps

# MySQL Configuration
MYSQL_HOST=localhost
MYSQL_DEFAULTS=/etc/mysql/debian.cnf
```

[Back To Top](#top)

## Commands <a name="commands"></a>

[Requirements](#requirements) | [Description](#description) | [Quick Start](#quick-start) | [Installation](#installation) | [Configuration](#configuration) | [Commands](#commands) | [Usage](#usage)

All commands are run via Docker/Podman. The general format is:

```bash
docker run --rm --env-file .env [volumes] ghcr.io/kpirnie/wmh-helper:latest [command] [arguments]
```

### Backup

**Command:** `backup`

**Required Arguments:** `--backup account|acct|application|app|database|db|other|all`

**Description:** Backup accounts, applications, databases, or custom paths to S3-compatible storage.

**Examples:**

```bash
# Backup everything (all databases and web applications)
docker run --rm --env-file .env \
  -v /home:/home:ro \
  -v /etc/mysql:/etc/mysql:ro \
  --network host \
  ghcr.io/kpirnie/wmh-helper:latest backup --backup all

# Backup specific application
docker run --rm --env-file .env \
  -v /home:/home:ro \
  --network host \
  ghcr.io/kpirnie/wmh-helper:latest backup --backup app --account myuser --app mysite

# Backup specific database
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

### Restore

**Command:** `restore`

**Description:** Interactive restore wizard that guides you through restoring backups.

**Example:**

```bash
docker run --rm -it --env-file .env \
  -v /home:/home \
  -v /tmp/restore:/tmp/restore \
  --network host \
  ghcr.io/kpirnie/wmh-helper:latest restore
```

### Image Optimization

**Command:** `optimages`

**Required Arguments:** `--optimize account|acct|application|app|other|all`

**Description:** Optimize images (PNG, JPG, GIF, WebP, SVG) to reduce file sizes.

**Examples:**

```bash
# Optimize all images
docker run --rm --env-file .env \
  -v /home:/home \
  ghcr.io/kpirnie/wmh-helper:latest optimages --optimize all

# Optimize specific application
docker run --rm --env-file .env \
  -v /home:/home \
  ghcr.io/kpirnie/wmh-helper:latest optimages --optimize app --account myuser --app mysite

# Optimize custom paths
docker run --rm --env-file .env \
  -v /var/www:/var/www \
  ghcr.io/kpirnie/wmh-helper:latest optimages --optimize other --paths /var/www/images
```

### Malware Scanning

**Command:** `scan`

**Required Arguments:** `--scan account|acct|application|app|other|all`

**Optional Flags:**
- `--auto_quarantine` - Automatically quarantine detected threats
- `--auto_clean` - Automatically clean detected threats

**Examples:**

```bash
# Scan everything
docker run --rm --env-file .env \
  -v /home:/home:ro \
  ghcr.io/kpirnie/wmh-helper:latest scan --scan all

# Scan and auto-quarantine
docker run --rm --env-file .env \
  -v /home:/home \
  ghcr.io/kpirnie/wmh-helper:latest scan --scan all --auto_quarantine

# Scan specific application
docker run --rm --env-file .env \
  -v /home:/home:ro \
  ghcr.io/kpirnie/wmh-helper:latest scan --scan app --account myuser --app mysite
```

### WordPress Updates

**Command:** `update`

**Required Arguments:** `--update wordpress`

**Optional Flags:** `--include_plugins`

**Description:** Update WordPress core (and plugins if flag is set) with automatic backup and rollback on failure.

**Examples:**

```bash
# Update WordPress core only
docker run --rm --env-file .env \
  -v /home:/home \
  --network host \
  ghcr.io/kpirnie/wmh-helper:latest update --update wordpress

# Update WordPress core and plugins
docker run --rm --env-file .env \
  -v /home:/home \
  --network host \
  ghcr.io/kpirnie/wmh-helper:latest update --update wordpress --include_plugins
```

### Free Memory

**Command:** `freem`

**Description:** Clear system caches and free unused memory.

**Example:**

```bash
docker run --rm --privileged \
  ghcr.io/kpirnie/wmh-helper:latest freem
```

[Back To Top](#top)

## Usage <a name="usage"></a>

[Requirements](#requirements) | [Description](#description) | [Quick Start](#quick-start) | [Installation](#installation) | [Configuration](#configuration) | [Commands](#commands) | [Usage](#usage)

### Using Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  kp-helper:
    image: ghcr.io/kpirnie/wmh-helper:latest
    container_name: kp-hosting-helper
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

Run commands:

```bash
# Backup everything
docker-compose run --rm kp-helper backup --backup all

# Restore interactively
docker-compose run --rm kp-helper restore

# Optimize images
docker-compose run --rm kp-helper optimages --optimize all

# Scan for malware
docker-compose run --rm kp-helper scan --scan all
```

### Automated Backups with Cron

Create a systemd service and timer:

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

[Install]
WantedBy=multi-user.target
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

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable kp-backup.timer
sudo systemctl start kp-backup.timer

# Check status
sudo systemctl status kp-backup.timer
sudo systemctl list-timers
```

### Automated Backups with Cron (Traditional)

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /usr/bin/docker run --rm --env-file /opt/kp-helper/.env -v /home:/home:ro -v /etc/mysql:/etc/mysql:ro --network host ghcr.io/kpirnie/wmh-helper:latest backup --backup all >> /var/log/kp-backup.log 2>&1
```

### Volume Mounts

Common volume mount patterns:

```bash
# Read-only mounts for backups (recommended)
-v /home:/home:ro
-v /etc/mysql:/etc/mysql:ro

# Read-write for operations that modify files
-v /home:/home                    # Image optimization, WordPress updates
-v /tmp/restore:/tmp/restore      # Restore operations

# Mount specific paths
-v /home/user1:/home/user1:ro     # Single user
-v /var/www:/var/www:ro           # Web root
```

### Network Modes

```bash
# Host network (for MySQL access on localhost)
--network host

# Bridge network with custom MySQL host
--network bridge -e MYSQL_HOST=mysql.example.com
```

### Security Considerations

1. **Protect your .env file:**
   ```bash
   chmod 600 .env
   ```

2. **Use read-only mounts when possible:**
   ```bash
   -v /home:/home:ro  # :ro = read-only
   ```

3. **Store .env outside web root:**
   ```bash
   /opt/kp-helper/.env  # Good
   /var/www/.env        # Bad
   ```

4. **Use secrets management for production:**
   - Docker Secrets
   - Kubernetes Secrets
   - HashiCorp Vault

### Troubleshooting

**View container logs:**
```bash
docker logs kp-hosting-helper
```

**Run interactively for debugging:**
```bash
docker run --rm -it --env-file .env \
  -v /home:/home \
  --network host \
  --entrypoint /bin/bash \
  ghcr.io/kpirnie/wmh-helper:latest
```

**Test configuration:**
```bash
docker run --rm --env-file .env \
  ghcr.io/kpirnie/wmh-helper:latest backup --help
```

**Update to latest image:**
```bash
docker pull ghcr.io/kpirnie/wmh-helper:latest
```

[Back To Top](#top)

## License

MIT License

See [LICENSE](LICENSE) file for details.

## Support

For issues, questions, or contributions, please visit:
- GitHub: https://github.com/kpirnie/hosting-helper
- Issues: https://github.com/kpirnie/hosting-helper/issues

[Back To Top](#top)