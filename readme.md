# KP Hosting Helper App <a name="top"></a>

[Requirements](#requirements) | [Description](#description) | [Install / Update](#install) | [Config](#config) | [Commands](#commands) | [Usage](#usage)

Python 3 app to control and configure some useful items in a web server.

## Requirements <a name="requirements"></a>

[Requirements](#requirements) | [Description](#description) | [Install / Update](#install) | [Config](#config) | [Commands](#commands) | [Usage](#usage)

**Operating System**

- Ubuntu
    - 18.04 - Fully Tested
    - 20.04 - Fully Tested
    - 22.04 - Fully Tested
- Windows 10 & 11
    - Fully tested in WSL
        - Ubuntu 18.04, 20.04, 22.04
- Mac OS
    - untested

**Python 3.6+**

**CLI and Shell Access**

[Back To Top](#top)

## Description <a name="description"></a>

[Requirements](#requirements) | [Description](#description) | [Install / Update](#install) | [Config](#config) | [Commands](#commands) | [Usage](#usage)

This is a compiled Python application for managing some functionality on web servers.  It is compiled on both Ubuntu 18.04 LTS, Ubuntu 20.04 LTS, & Ubuntu 20.04 LTS utilizing the clang C compiler. 

It includes:

- backup (automatable thru cron) and restore capabilites to S3 compatible storage systems
- image optimization techniques for jpg, gif, webp, png, and svg images
- anti-virus and anti-malware scanning
- system & wordpress automatable updates 
- some minor performance enhancements for mysql, php, and nginx on RunCloud based servers

[Back To Top](#top)

## Install / Update <a name="install"></a>

[Requirements](#requirements) | [Description](#description) | [Install / Update](#install) | [Config](#config) | [Commands](#commands) | [Usage](#usage)

Download the app from the releases here: <a href="https://gitlab.com/kp-development/python/kp-hosting-helper/-/releases">https://gitlab.com/kp-development/python/kp-hosting-helper/-/releases</a>

The releases are named with this convention: `NAME` - `OS.VERION` - `APP.VERSION`, please pay attention to the `OS.VERSION` so you download the proper version for the system you want to run this on.

Once downloaded, I would suggest renaming the version you downloaded to simply be `kp`.  All references to the app including the usage commands below reference this as the app, so just to avoid confusion...

Once downloaded run the following commands to install:

- `sudo chmod +x kp`
- `sudo mv kp /usr/bin/`
- `sudo kp setup --setup system` 
- `sudo kp setup --setup app`
    - You will be prompted to configure, or re-configure the app.  Please pay attention.

To update the app, download as instructed above, and run the following commands to update:

- `sudo chmod +x kp`
- `sudo mv kp /usr/bin/`
- `sudo kp update --update system` 
- `sudo kp update --update app`

[Back To Top](#top)

## Configuration <a name="config"></a>

[Requirements](#requirements) | [Description](#description) | [Install / Update](#install) | [Config](#config) | [Commands](#commands) | [Usage](#usage)

In order to utilize this app's backup and restore functionality, we must configure the app to communicate with your S3 compatible cloud storage, and mysql.  This information is stored in a hidden file on the system this app is installed on.

To configure or update your configuration, please run the following command: `kp config` and pay attention to the prompts.

- **How many days should backups be retained?**
    - How many days should a full backup set be retained?  This may keep snapshots older than the configured amount of days, this is done to keep full backup respositories fully intact.  Once the full backup time has expired, it will be removed.
    - **Default:** 30 days
- **Enter an ecryption key to use**
    - All backups are encrypted prior to uploading to your S3 compatible storage.  In order to do so, a key or hash is required.
    - **Default:** A random string between 32 and 64 characters
    - You will be shown this key at the end of the configuration in case you need to use it to remotely restore backups from this system to another.
- **Enter your S3 API Key**
    - This is the API key you will need to gather from your S3 compatible storage provider.  Please see your provider, or Google how to get this key.
    - **NOTE:** If you do not provide this key, you will not be able to backup or restore.
- **Enter your S3 API Secret**
    - This is the API secret you will need to gather from your S3 compatible storage provider.  Please see your provider, or Google how to get this key.
    - **NOTE:** If you do not provide this key, you will not be able to backup or restore.
- **Enter your S3 Endpoint**
    - This is the endpoint the backup system connects to you will need to gather this from your S3 compatible storage provider.  Please see your provider, or Google how to get this endpoint.
    - **Default:** s3.amazonaws.com
- **Enter your S3 Bucket**
    - This is the bucket where your backups will be stored in your S3 compatible storage provider.  Please see your provider, or Google how to get this bucket, or how to setup a new one.
    - **NOTE:** If you do not provide this bucket, you will not be able to backup or restore.
- **Enter the S3 Region**
    - This is the region configured for your S3 compatible storage.  Please see your provider, or Google how to get this region.
    - **Default:** us-east-1
- **Enter a name for the backup**
    - You can name this however you like, personally I tend to use my systems hostname so I can keep my backups organized.
    - **Default:** Your systems hostname'
- **Backup starting path**
    - The path where your systems users have their homes
    - **Default:** `/home/`
- **Backup application name**
    - Because I primarily use this to backup my web applications, this would be that parent directory on your server where the web applications are stored
    - **Default:** `webapps`
- **Enter your mysql host server**
    - If you intend to backup mysql databases, enter the host server location for them.
    - **Default:** `localhost`
- **Enter your mysql defaults file path**
    - If you intend to backup mysql databases, the backup system will need to know how to run some administrative commands... primarily `mysqldump` in order to back them up.  The safest way to do this is to utilize the local servers mysql defaults file.
    - If you do not put this in, you will be prompted to provide an admin user account.
    - **Default:** `null`

[Back To Top](#top)

## Commands <a name="commands"></a>

[Requirements](#requirements) | [Description](#description) | [Install / Update](#install) | [Config](#config) | [Commands](#commands) | [Usage](#usage)

All commands need to be run in shell on your server, and start with a simple call to the app: `kp`

### Setup

**Command:** `setup`

**Required Arguments:**

`--setup app|system`

**Description:**

Sets up the app or system based on the argument passed.  

- `app` 
    - installs the necessary modules for the app to run properly
- `system`
    - installs the necessary apps for the system to run at peak performance
    - if your server is a RunCloud managed server, will also install some performance tweaks for php, mysql, and nginx based on the memory and CPU your server utilizes

**Example:** `sudo kp setup --setup app`

### Update

**Command:** `update`

**Required Arguments:**

`--update app|system|wordpress`

**Description:**

Updates the app, system, or wordpress apps based on the argument passed.  

- `app` 
    - updates and upgrades the necessary modules for the app to run properly
- `system`
    - updates and upgrades the necessary apps for the system to run at peak performance
- `wordpress`
    - updates all wordpress installs on the server to the latest Core version after taking a full backup of each install.  Once the update is complete, the app will test the site to see if a sucessful response code is returned.  If not, it will automatically restore the app.
    - Include the flag `--include_plugins` to also include plugin updates.  They are run similar to the above core update.

**Example:** `sudo kp update --update wordpress --include_plugins`

### Configuration

**Command:** `config`

**Required Arguments:**

NONE

**Description:**

Runs the apps configurator.  Please see here for more information on what is required: [Config](#config)

**Example:** `sudo kp config`

### Backup

**Command:** `backup`

**Required Arguments:**

`--backup account|acct|application|app|database|db|other|all`

**Description:**

Backup an account, an application, a database, or any other path(s).  `all` will backup all databases and web applications on the server based on your configured paths.  

- `account|acct` 
    - Additional Argument(s): `--account|acct`
    - The account is required in order to back up an account, if you do not specify this additional argument, you will be prompted to supply it.
- `application|app`
    - Additional Argument(s): `--account|acct`, `--application|app`
    - The account and application are required in order to back up an application, if you do not specify these additional arguments, you will be prompted to supply them.
- `database|db`
    - Additional Argument(s): `--database|db`
    - The dabatase name or `all` is required in order to backup a database, if you do not specify this additional argument, you will be prompted to supply it.
    - You can use `all` to backup all databases on the server
- `other`
    - Required Additional Argument(s): `--paths`
        - Specify a comman-delimited list of paths on your server to backup
        - This argument can also be included in any other backup method to include the specified paths as part of that backup
- `all`
    - Backs up all databases and web applications on the server based on your configured app paths
    - No other argument is necessary for this

**Example:** `sudo kp backup --backup app --account THE_ACCOUNT_NAME --app THE_APPNAME --paths /home/yourhome,/etc/mysql`

### Restore

**Command:** `restore`

**Required Arguments:**

NONE

**Description:**

Runs the backup restore methodolgy.  You will be prompted for everything, so please pay attention.

You can restore anything from another server that was backed up utilizing this, if you choose to do so, you will be prompted for that servers API Key, API Secret, Endpoint, Bucket, Region, Name, and Hash used to encrypt it.

**Example:** `sudo kp restore`

### Optimages

**Command:** `optimages`

**Required Arguments:**

`--optimize account|acct|application|app|other|all`

**Description:**

Attempts to optimize all images specified in your additional argument. `all` will attempt to do so for all accounts and applications specified in your configuration.

We utilize the following server-side apps in order to perform all optimizations: optipng, jpegoptim, gifsicle, webp

- `account|acct` 
    - Additional Argument(s): `--account|acct`
    - The account is required in order to optimize its images, if you do not specify this additional argument, you will be prompted to supply it.
- `application|app`
    - Additional Argument(s): `--account|acct`, `--application|app`
    - The account and application are required in order to optimize their images, if you do not specify these additional arguments, you will be prompted to supply them.
- `other`
    - Required Additional Argument(s): `--paths`
        - Specify a comman-delimited list of paths on your server to optimize the images for
        - This argument can also be included in any other optimize method to include the specified paths as part of that optimization
- `all`
    - Optimizes all images on the server based on your configured app paths
    - No other argument is necessary for this

**Example:** `sudo kp optimages --optimize app --account YOUR_ACCOUNT_NAME --app YOUR_APP_NAME --paths /home/yourhome,/etc/mysql`

### Freem

**Command:** `freem`

**Required Arguments:**

NONE

**Description:**

Attempts to clean system caches and free up un-used or zombie memory on the server.

**Example:** `sudo kp freem`

### Scan

**Command:** `scan`

**Required Arguments:**

`--scan account|acct|application|app|other|all`

**Description:**

Attempts to scan all locations specified in your additional argument for virii or malware. `all` will attempt to do so for all accounts and applications specified in your configuration.

- `account|acct` 
    - Additional Argument(s): `--account|acct`
    - The account is required in order to scan, if you do not specify this additional argument, you will be prompted to supply it.
- `application|app`
    - Additional Argument(s): `--account|acct`, `--application|app`
    - The account and application are required in order to scan, if you do not specify these additional arguments, you will be prompted to supply them.
- `other`
    - Required Additional Argument(s): `--paths`
        - Specify a comman-delimited list of paths on your server to scan
        - This argument can also be included in any other scan method to include the specified paths as part of that scan
- `all`
    - Scans all apps on the server based on your configured app paths
    - No other argument is necessary for this

**Example:** `sudo kp scan --scan app --account YOUR_ACCOUNT_NAME --app YOUR_APP_NAME --paths /home/yourhome,/etc/mysql`

[Back To Top](#top)

## Usage <a name="usage"></a>

[Requirements](#requirements) | [Description](#description) | [Install / Update](#install) | [Config](#config) | [Commands](#commands) | [Usage](#usage)

```
--------------------------------------------------------------------------------------
kp [setup|update|config|backup|restore|optimages|freem|scan] [additional arguments]
--------------------------------------------------------------------------------------
setup:
    --setup: [app|system]
    Setup the app or system with additional apps or configurations
update:
    --update: [app|system|wordpress]
        if wordpress: --include_plugins
    Update the app, system, or wordpress
config:
    FOLLOW THE PROMPTS
backup:
    --backup: [account|acct|application|app|database|db|other|all]
    Backup an account, an application, a database, or any other path(s)
    ALL will backup all accounts, apps, and databases as configured by your app configuration
restore:
    FOLLOW THE PROMPTS
optimages:
    --optimize: [account|acct|application|app|other|all]
    Optimize images for an account, an application, a database, or any other path(s)
    ALL will optimize images for all accounts and apps as configured by your app configuration
freem:
    NO OPTIONS
scan:
    --scan: [account|acct|application|app|other|all]
        --auto_quarantine
        --auto_clean
    Scan an account, an application, or any other path(s) for malware or virii
    ALL will scan all accounts and apps as configured by your app configuration
SEMI-GLOBAL:
    --paths: Command-delimited string of paths
        NOTE: only available for backup, optimizing images, or scanning
    --acct|account: Account Name
        NOTE: only pass if backing up, optimizing images, or scanning automatically
    --app|application: Application Name
        NOTE: only pass if backing up, optimizing images, or scanning automatically
    --db|--database: Database Name
        NOTE: only pass if backing up automatically
--------------------------------------------------------------------------------------
```

[Back To Top](#top)
