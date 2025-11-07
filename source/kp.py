#!/usr/bin/env python3

# some necessary imports
import os, argparse, sys, time

# import the argument parser raw text helper
from argparse import RawTextHelpFormatter

# import the common class
from work.common.common import KP_Common
common = KP_Common( )

# get the python version. This will only work with v3.6+
_py_ver = sys.version_info
if _py_ver[0] < 3 and _py_ver[1] < 6:
    common.my_print( "info", ( "*" * 52 ) )
    common.my_print( "error", "You must be running at least Python 3.6" )
    common.my_print( "error", "You are currently running version: {}.{}.{}".format( _py_ver[0], _py_ver[1], _py_ver[2] ) )
    common.my_print( "info", ( "*" * 52 ) )
    sys.exit( )

# make sure we are a sudo user before we go any further
is_su = os.getuid( )
if is_su != 0:
    common.my_print( "info", ( "*" * 52 ) )
    common.my_print( "error", "You must run this as root, or at least a sudo user.\nPlease login as the root/sudo account and try again." )
    common.my_print( "info", ( "*" * 52 ) )
    sys.exit( )

# wrap all the actions in a try block
try:

    # fire up the argument parser
    # Updated usage to include mount action with all options
    _args = argparse.ArgumentParser( formatter_class=RawTextHelpFormatter, usage='''
--------------------------------------------------------------------------------------
\033[92mkp [backup|restore|mount|optimages|freem|scan|update]\033[37m \033[94m[additional arguments]\033[37m
--------------------------------------------------------------------------------------
\033[94mbackup\033[37m:
    \033[92m--backup\033[37m: [account|acct|application|app|database|db|other|all]
    Backup an account, an application, a database, or any other path(s)
    \033[94mALL\033[37m will backup all accounts, apps, and databases as configured by your app configuration
\033[94mrestore\033[37m:
    FOLLOW THE PROMPTS
\033[94mmount\033[37m:
    \033[92m--source\033[37m: [optional] S3 path or relative path to mount
    \033[92m--destination\033[37m: [optional] Local path where to mount the backup
    \033[92m--unmount\033[37m: Path to unmount
    \033[92m--list\033[37m: List all active mounts
    \033[92m--foreground\033[37m: Run mount in foreground (blocks until CTRL-C)
    Mount a backup repository to a local directory for browsing
    Default behavior: Mounts in background, requires manual unmount
    If no arguments provided, interactive menu will guide you
\033[94moptimages\033[37m:
    \033[92m--optimize\033[37m: [account|acct|application|app|other|all]
    Optimize images for an account, an application, a database, or any other path(s)
    \033[94mALL\033[37m will optimize images for all accounts and apps as configured by your app configuration
\033[94mfreem\033[37m:
    NO OPTIONS
\033[94mscan\033[37m:
    \033[92m--scan\033[37m: [account|acct|application|app|other|all]
        \033[92m--auto_quarantine\033[37m
        \033[92m--auto_clean\033[37m
    Scan an account, an application, or any other path(s) for malware or virii
    \033[94mALL\033[37m will scan all accounts and apps as configured by your app configuration
\033[94mupdate\033[37m:
    \033[92m--update\033[37m: [wordpress]
        \033[94mif wordpress\033[37m: \033[92m--include_plugins\033[37m
    Update wordpress installations
\033[94mSEMI-GLOBAL\033[37m:
    \033[92m--paths\033[37m: Command-delimited string of paths
        \033[94mNOTE\033[37m: only available for backup, optimizing images, or scanning
    \033[92m--acct|account\033[37m: Account Name
        \033[94mNOTE\033[37m: only pass if backing up, optimizing images, or scanning automatically
    \033[92m--app|application\033[37m: Application Name
        \033[94mNOTE\033[37m: only pass if backing up, optimizing images, or scanning automatically
    \033[92m--db|--database\033[37m: Database Name
        \033[94mNOTE\033[37m: only pass if backing up automatically
--------------------------------------------------------------------------------------
Please see the readme for more info''', add_help=False, allow_abbrev=False )

    # our action argument - added 'mount' to choices
    _args.add_argument( "action", choices=[ "backup", "restore", "mount", 'optimages', 'freem', 'scan', 'update' ], help=argparse.SUPPRESS )

    # mount-specific arguments
    _args.add_argument( "--source", help=argparse.SUPPRESS )  # source path to mount
    _args.add_argument( "--destination", help=argparse.SUPPRESS )  # destination mount point
    _args.add_argument( "--unmount", help=argparse.SUPPRESS )  # path to unmount
    _args.add_argument( "--list", "--list-mounts", dest="list_mounts", action='store_true', help=argparse.SUPPRESS )  # list active mounts
    _args.add_argument( "--foreground", action='store_true', help=argparse.SUPPRESS )  # run in foreground mode

    # update what?
    _args.add_argument( "--update", choices=[ "wordpress" ], help=argparse.SUPPRESS )
    
    # include plugins for wordpress update?
    _args.add_argument( "--include_plugins", action='store_true', help=argparse.SUPPRESS )

    # backup what
    _args.add_argument( "--backup", choices=[ "account", "acct", "application", "app", "database", "db", "other", "all" ], help=argparse.SUPPRESS )

    # optimize what images?
    _args.add_argument( "--optimize", choices=[ "account", "acct", "application", "app", "other", "all" ], help=argparse.SUPPRESS )

    # scanning what?
    _args.add_argument( "--scan", choices=[ "account", "acct", "application", "app", "other", "all" ], help=argparse.SUPPRESS )

    # if scanning, add a flag to auto-quarantine hits
    _args.add_argument( "--auto_quarantine", action='store_true', help=argparse.SUPPRESS )

    # if scanning, add a flag to auto-clean hits
    _args.add_argument( "--auto_clean", action='store_true', help=argparse.SUPPRESS )

    # paths argument, comma-delimited list of paths
    _args.add_argument( "--paths", help=argparse.SUPPRESS )

    # extra arguments for automated backups, image optimizations, and scans
    _args.add_argument( "--acct", "--account", dest="account", help=argparse.SUPPRESS )
    _args.add_argument( "--app", "--application", dest="application", help=argparse.SUPPRESS )
    _args.add_argument( "--db", "--database", dest="database", help=argparse.SUPPRESS )

    # if no arguments have been passed, quit, and show the help
    if not len( sys.argv ) > 1:

        # throw an error message here
        common.my_print( "info", ( "*" * 52 ) )
        common.my_print( "error", "You must pass at least 1 argument." )
        print( )
        _args.print_help( )
        common.my_print( "info", ( "*" * 52 ) )
        sys.exit( )

    # otherise we're good here
    else:
        
        # now that we know we have an action, parse
        _the_args = _args.parse_args( )

        # setup the action
        _action = _the_args.action.lower( )

        # setup the class to run based on the action requested
        _cls = common.class_for_name( _action )( _args )

        # run what we need to
        _cls.run( )

        # clean up
        del _cls
        
# catch the keyboard interrupt
except KeyboardInterrupt:

    # show a message then exit
    print( )
    common.my_print( "info", ( "*" * 52 ) )
    common.my_print( "success", "Exitting the app, please hold." )
    common.my_print( "info", ( "*" * 52 ) )
    time.sleep( 5 )
    sys.exit( )