#!/usr/bin/env python3

class KP_Common:

    # initialize us
    def __init__( self ):

        # import os and json modules
        import os, json

        # config file path
        self.config_file = "/root/.kpbr"

        # figure out how many worker threads we want for these tasks
        self.allowed_threads = int( min( 32, os.cpu_count( ) + 4 ) / 2 )

        # set a temporary restore location
        self.tmp_restore_location = "/tmp/restore/"

        # get the machine's hostname
        self.hostname = os.uname( )[1]

        # hold our config variables
        self.key = None
        self.secret = None
        self.hash = None
        self.endpoint = None
        self.bucket = None
        self.region = None
        self.retention = None
        self.name = None
        self.path_start = None
        self.path_for_apps = None
        self.mysql_host = None
        self.mysql_defaults = None
        self.mysql_user = None
        self.mysql_password = None

        # if the config file exists
        if os.path.exists( self.config_file ):

            # open the file as read-only
            with open( self.config_file ) as _settings:

                # load and parse as json
                _config = json.load( _settings )

                # populate
                self.key = _config[0].get( "key" )
                self.secret = _config[0].get( "secret" )
                self.hash = _config[0].get( "hash" )
                self.endpoint = _config[0].get( "endpoint" )
                self.bucket = _config[0].get( "bucket" )
                self.region = _config[0].get( "region" )
                self.retention = _config[0].get( "retention" )
                self.name = _config[0].get( "name" )
                self.path_start = _config[0].get( "path_start" )
                self.path_for_apps = _config[0].get( "path_for_apps" )
                self.mysql_host = _config[0].get( "mysql_host" )
                self.mysql_defaults = _config[0].get( "mysql_defaults" )
                self.mysql_user = _config[0].get( "mysql_user" )
                self.mysql_password = _config[0].get( "mysql_password" )

        # the full backup repository
        self.backup_repo_prefix = "s3://{}/{}/{}/".format( self.endpoint, self.bucket, self.name )
        
        # the backup repo without the self.name
        self.backup_repo = "s3://{}/{}/".format( self.endpoint, self.bucket )

        # the backup path for apps
        self.backup_path_app = "{}apps/".format( self.backup_repo_prefix )

        # the backup path for databases
        self.backup_path_db = "{}database/".format( self.backup_repo_prefix )

        # the backup path for other
        self.backup_path_other = "{}other/".format( self.backup_repo_prefix )

        # format the primary command string, cleanup serverside caches
        self.primary_command = "restic --no-lock --cleanup-cache -r {}"

    # run the actual backup
    def backup_run( self, _repo, _path ):

        # setup the full primary command
        _primary = self.primary_command.format( _repo )

        # setup the full backup command
        _cmd = "{} backup {}".format( _primary, _path )

        # run the command
        self.execute( _cmd )

    # run the backup initialization
    def backup_init( self, _repo ):

        # THE repo
        _the_repo = self.primary_command.format( _repo )

        # setup the command to run
        _cmd = "{} snapshots > /dev/null || {} init".format( _the_repo, _the_repo )

        # run the initialization command
        self.execute( _cmd )

    # run backup clean up
    def backup_cleanup( self, _repo ):

        # THE repo
        _the_repo = self.primary_command.format( _repo )

        # setup the command to run
        _cmd = "{} forget --keep-daily {} --prune".format( _the_repo, self.retention, self.retention )

        # run the cleanup command
        self.execute( _cmd )

    # change ownership
    def change_path_ownership( self, _path, _usr, _grp ):

        # import the sh utility
        import shutil

        # chown the path
        shutil.chown( _path, _usr, _grp )

    # get the path owner username
    def path_owner_user( self, _path ):
        
        # import our path library
        from pathlib import Path

        # catch an exception
        try:
            
            # get the actual path as an object
            path = Path( _path )

            # return the owner
            return path.owner( )
        except:

            # default as root: backup after restore from other machine fails because the user id does not match
            return "root"

    # get the path owner group name
    def path_owner_group( self, _path ):

        # import our path library
        from pathlib import Path

        # catch an exception
        try:
            
            # get the actual path as an object
            path = Path( _path )

            # return the group
            return path.group( )
        except:

            # default as root: backup after restore from other machine fails because the user id does not match
            return "root"

    # windows allowed paths
    def format_path( self, _path ):

        # make sure we're not a None
        if _path is not None:

            # return a quoted string for the path
            return '"' + _path + '"'

    # execute a shell command
    def execute( self, _cmd, _quiet = True ):

        # import the subprocess module
        import subprocess

        # we don't want the output from this, so run it quietly
        if _quiet:

            # execute the command silently
            subprocess.call( [ _cmd ], shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL )
        else:

            # we do want the output
            return subprocess.check_output( [ _cmd ], shell=True )

    # our pretty printer ;)
    def my_print( self, _type, _str ):

        # default to white, or reset
        _reset = "\033[37m"

        # if it's an error
        if _type.lower( ) == "error":

            # red
            _prefix = "\033[91m"
        
        # if it's a success
        if _type.lower( ) == "success":

            # green
            _prefix = "\033[92m"

        # if it's a informative message
        if _type.lower( ) == "info":

            # blue
            _prefix = "\033[94m"

        # print the output based on the selected message type
        print( _prefix + _str + _reset )

    # return the class from our action
    def class_for_name( self, _our_action ):

        # import the importlib module
        import importlib

        # load the module, will raise ImportError if module cannot be loaded
        m = importlib.import_module( "work.{}.{}".format( _our_action, _our_action ) )

        # get the class, will raise AttributeError if class cannot be found
        c = getattr( m, "KP_{}".format( _our_action.capitalize( ) ) )

        # return
        return c

    # run the "other" backup
    def run_other_backup( self, paths ):

        # import the "other" backup module
        from work.backup.other import KP_Backup_Other

        # fire it up
        _other = KP_Backup_Other( paths )

        # run it
        _other.run( )

        # clean up
        del _other

    # pull our help message