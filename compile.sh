#!/usr/bin/env bash

# get the version number
TMPVER=`cat /etc/os-release | grep VERSION_ID`
VER=$(echo "$TMPVER" | sed "s/VERSION_ID=//")
VER=${VER:1:-1}

# make sure our packages are installed
apt-get install -y zip python3-dev python3-pip

# let's make sure pip is up to date
python3 -m pip install --upgrade -r requirements.txt --break-system-packages

# get the path to this script
CODEPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )";

# make a directory for the releases
mkdir -p $CODEPATH/release;

# try to compile
pyinstaller \
    --hidden-import boto3 \
    --hidden-import work.backup.account \
    --hidden-import work.backup.all \
    --hidden-import work.backup.app \
    --hidden-import work.backup.backup \
    --hidden-import work.backup.database \
    --hidden-import work.backup.other \
    --hidden-import work.freem.freem \
    --hidden-import work.optimages.optimages \
    --hidden-import work.restore.restore \
    --hidden-import work.scan.scan \
    --hidden-import work.setup.app \
    --hidden-import work.setup.setup \
    --hidden-import work.setup.system \
    --hidden-import work.update.app \
    --hidden-import work.update.system \
    --hidden-import work.update.update \
    --hidden-import work.update.wordpress \
    --distpath $CODEPATH/release/ \
    --clean \
    -F \
    -n kp-$VER \
    -p $CODEPATH/source/ \
$CODEPATH/source/kp.py

# find and remove the PYC files
find . -type f -name "*.pyc" -exec rm -f {} \;
find . -type d -name "__pycache*" -exec rm -rf {} \;

# remove the build directory
rm -rf $CODEPATH/build

# set the executable bit
chmod +x $CODEPATH/release/kp-$VER

# now zip up the mount scripts
#zip mount-scripts.zip mount-backup.sh .mb-source.sh 1> /dev/null

# move the zip to the release folder
#mv mount-scripts.zip $CODEPATH/release/
