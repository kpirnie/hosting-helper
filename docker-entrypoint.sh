#!/bin/bash
set -e

# Generate config file from environment variables
generate_config() {
    local config_file="/root/.kpbr"
    
    # Generate random hash if not provided
    if [ -z "$RESTIC_PASSWORD" ]; then
        RESTIC_PASSWORD=$(tr -dc 'A-Za-z0-9' < /dev/urandom | head -c 48)
        echo "Generated RESTIC_PASSWORD: $RESTIC_PASSWORD"
    fi
    
    # Use hostname as backup name if not provided
    if [ -z "$KP_BACKUP_NAME" ]; then
        KP_BACKUP_NAME=$(hostname)
    fi
    
    # Create JSON config
    cat > "$config_file" <<EOF
[
    {
        "key": "${KP_S3_KEY}",
        "secret": "${KP_S3_SECRET}",
        "hash": "${RESTIC_PASSWORD}",
        "endpoint": "${KP_S3_ENDPOINT}",
        "bucket": "${KP_S3_BUCKET}",
        "region": "${KP_S3_REGION}",
        "retention": ${KP_RETENTION_DAYS},
        "name": "${KP_BACKUP_NAME}",
        "path_start": "${KP_PATH_START}",
        "path_for_apps": "${KP_PATH_FOR_APPS}",
        "mysql_host": "${KP_MYSQL_HOST}",
        "mysql_defaults": "${KP_MYSQL_DEFAULTS}",
        "mysql_user": "${KP_MYSQL_USER}",
        "mysql_password": "${KP_MYSQL_PASSWORD}"
    }
]
EOF
    
    # Set restrictive permissions
    chmod 600 "$config_file"
    
    echo "Configuration file created at $config_file"
}

# Check if config needs to be generated
if [ ! -f "/root/.kpbr" ] || [ "${FORCE_CONFIG_REGEN}" = "true" ]; then
    generate_config
fi

# Set AWS credentials in environment if provided
if [ -n "$KP_S3_KEY" ]; then
    export AWS_ACCESS_KEY_ID="$KP_S3_KEY"
fi

if [ -n "$KP_S3_SECRET" ]; then
    export AWS_SECRET_ACCESS_KEY="$KP_S3_SECRET"
fi

if [ -n "$KP_S3_REGION" ]; then
    export AWS_DEFAULT_REGION="$KP_S3_REGION"
fi

# Execute the main application
exec python3 /app/kp.py "$@"
