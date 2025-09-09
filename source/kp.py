#!/usr/bin/env python3

# some necessary imports
import os, argparse, sys, time

# import the argument parser raw text helper
from argparse import RawTextHelpFormatter

# import the common class
from work.common.common import KP_Common
common = KP_Common( )

# get the python version.    This will only work with v3.6+
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
    _args = argparse.ArgumentParser( formatter_class=RawTextHelpFormatter, usage='''
--------------------------------------------------------------------------------------
\033[92mkp [setup|update|config|backup|restore|optimages|freem|scan]\033[37m \033[94m[additional arguments]\033[37m
--------------------------------------------------------------------------------------
\033[94msetup\033[37m:
    \033[92m--setup\033[37m: [app|system]
    Setup the app or system with additional apps or configurations
\033[94mupdate\033[37m:
    \033[92m--update\033[37m: [app|system|wordpress]
        \033[94mif wordpress\033[37m: \033[92m--include_plugins\033[37m
    Update the app, system, or wordpress
\033[94mconfig\033[37m:
    FOLLOW THE PROMPTS
\033[94mbackup\033[37m:
    \033[92m--backup\033[37m: [account|acct|application|app|database|db|other|all]
    Backup an account, an application, a database, or any other path(s)
    \033[94mALL\033[37m will backup all accounts, apps, and databases as configured by your app configuration
\033[94mrestore\033[37m:
    FOLLOW THE PROMPTS
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

    # our action argument
    _args.add_argument( "action", choices=[ "setup", "update", "config", "backup", "restore", 'optimages', 'freem', 'scan' ], help=argparse.SUPPRESS )

    # setup what?
    _args.add_argument( "--setup", choices=[ "app", "system" ], help=argparse.SUPPRESS )

    # update what?
    _args.add_argument( "--update", choices=[ "app", "system", "wordpress" ], help=argparse.SUPPRESS )
    
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
