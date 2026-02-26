#!/usr/bin/env bash

# Detect the OS for naming
if [ -f /etc/debian_version ]; then
    if grep -q "Ubuntu" /etc/issue; then
        OS_NAME="ubuntu"
        OS_VER=$(lsb_release -rs | cut -d. -f1)
    else
        OS_NAME="debian"
        OS_VER=$(cat /etc/debian_version | cut -d. -f1)
    fi
else
    OS_NAME="unknown"
    OS_VER="0"
fi

# make sure our packages are installed
apt-get update
apt-get install -y zip python3-dev python3-pip build-essential binutils patchelf

# let's make sure pip is up to date
python3 -m pip install --upgrade -r requirements.txt --break-system-packages

# get the path to this script
CODEPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )";

# make a directory for the releases
mkdir -p $CODEPATH/release;

# Create a more portable spec file
cat > $CODEPATH/kp.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['source/kp.py'],
    pathex=['source/'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'boto3',
        'botocore',
        'botocore.session',
        'botocore.client',
        's3transfer',
        'pymysql',
        'apt',
        'psutil',
        'simple_term_menu',
        'dateutil',
        'dateutil.parser',
        'json',
        'subprocess',
        'multiprocessing',
        'multiprocessing.pool',
        'threading',
        'pathlib',
        'shutil',
        'xml.dom.minidom',
        'requests',
        'urllib3',
        'work.backup.account',
        'work.backup.all',
        'work.backup.app',
        'work.backup.backup',
        'work.backup.database',
        'work.backup.other',
        'work.common.common',
        'work.common.menu',
        'work.config.config',
        'work.freem.freem',
        'work.mount.mount',
        'work.optimages.optimages',
        'work.restore.restore',
        'work.scan.scan',
        'work.setup.app',
        'work.setup.setup',
        'work.setup.system',
        'work.update.app',
        'work.update.system',
        'work.update.update',
        'work.update.wordpress',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'scipy'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='kp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
EOF

# Use the spec file for compilation
pyinstaller --distpath $CODEPATH/release/ --clean $CODEPATH/kp.spec

# find and remove the PYC files
find . -type f -name "*.pyc" -exec rm -f {} \;
find . -type d -name "__pycache*" -exec rm -rf {} \;

# remove the build directory
rm -rf $CODEPATH/build
rm -f $CODEPATH/kp.spec

# set the executable bit
chmod +x $CODEPATH/release/kp

echo "Binary compiled as: kp"
echo ""
echo "IMPORTANT NOTES:"
echo "1. This binary still requires system tools: mariadb/mysql, restic, etc."
echo "2. For maximum compatibility, install these packages on target systems:"
echo "   apt-get install mariadb-client restic optipng jpegoptim gifsicle webp"
echo "3. Or create a Docker container for true portability"
