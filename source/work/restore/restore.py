#!/usr/bin/env python3

# common imports
import os, sys, glob, getpass, shutil

from subprocess import Popen

class KP_Restore:

    # initialize us
    def __init__( self, _args = None ):

        # we'll need our commmon class in here for some items, so import it now
        from work.common.common import KP_Common

        # let's set the class to a class wide variable so we can use it later on if we need
        self.common = KP_Common( )

        # the s3 key
        self.s3_key = self.common.key

        # the s3 secret
        self.s3_secret = self.common.secret

        # the s3 endpoint
        self.s3_endpoint = self.common.endpoint

        # the s3 bucket
        self.s3_bucket = self.common.bucket

        # the s3 region
        self.s3_region = self.common.region

        # get the server/backup name
        self.bu_name = self.common.name

        # get the associated hash
        self.bu_hash = self.common.hash

        # the temporary mount location, unless specified in "BROWSE"
        self.temp_mount_path = "/tmp/backup-mount/"

        # hold the internals
        self.account = ""
        self.app = ""
        self.database = ""

    # destroyer!
    def __del__( self ):

        # clean up the common
        del self.common

        # clean up the defaults
        del self.s3_key, self.s3_secret, self.s3_endpoint, self.s3_bucket, self.s3_region, self.bu_name, self.bu_hash, self.temp_mount_path

        # clean up the internals
        del self.account, self.app, self.database

    # do what we need to do here
    def run( self ):

        # show a message
        self.common.my_print( "info", ( "*" * 52 ) )
        self.common.my_print( "success", "Please pay attention, you will be prompted for everything." )
        self.common.my_print( "info", ( "*" * 52 ) )

        # import our menu
        from work.common.menu import KP_Menu
        
        # fire up the menu class
        _menu = KP_Menu( )

        # is it a local backup or remote?
        _bu_location = _menu.location_menu( )

        # if our location is remote, we need some extra info... so gather it up now
        if _bu_location.lower( ) == "remote":

            # the s3 key
            self.s3_key = getpass.getpass( "Enter your S3 API Key: [null]" ) or None

            # the s3 secret
            self.s3_secret = getpass.getpass( "Enter your S3 API Secret: [null]" ) or None

            # the s3 endpoint
            self.s3_endpoint = input( "Enter your S3 Endpoint: [s3.amazonaws.com]" ) or "s3.amazonaws.com"

            # the s3 bucket
            self.s3_bucket = input( "Enter your S3 Bucket: [null]" ) or None

            # the s3 region
            self.s3_region = input( "Enter the S3 region: [us-east-1]" ) or "us-east-1"

            # get the server/backup name
            self.bu_name = input( "Please input the remote backups name: [null]" ) or None

            # get the associated hash
            self.bu_hash = getpass.getpass( "Please input the remote backups hash: [null]" ) or None

            # we need all of the above, otherwise exit with an error message
            if ( not self.s3_key ) or ( not self.s3_secret ) or ( not self.s3_endpoint ) or ( not self.s3_bucket ) or ( not self.s3_region ) or ( not self.bu_name ) or ( not self.bu_hash ):

                self.common.my_print( "info", ( "*" * 52 ) )
                self.common.my_print( "error", "All of this information is required in order\nto connect to your remote backup." )
                self.common.my_print( "info", ( "*" * 52 ) )
                sys.exit( )

        # what backup do we need to restore?
        _bu_type = _menu.backup_type_menu( )

        # how do we want to restore the backup?
        _bu_method = _menu.restore_method_menu( )

        # setup the common API environment variables
        os.environ["AWS_ACCESS_KEY_ID"] = self.s3_key
        os.environ["AWS_SECRET_ACCESS_KEY"] = self.s3_secret
        os.environ["AWS_DEFAULT_REGION"] = self.s3_region
        os.environ["RESTIC_PASSWORD"] = self.bu_hash

        # if the backup type is other
        if _bu_type.lower( ) == "other":

            # we're going to need to get the "other" path
            self.common.my_print( "info", "Please enter one of the paths you backed up that you wish to restore." )
            _bu_path = input( "Path: [null] " ) or None

            # require it
            if _bu_path is None or ',' in _bu_path.lower( ):

                print( "*" * 52 )
                self.common.my_print( "error", "You must enter a single path of your backed up files." )
                print( "*" * 52 )
                sys.exit( )

            # setup the repo path
            _repo_path = "{}{}".format( self.__repo_path( "other" ), _bu_path )

        # it's everything else
        else:

            # if we're restoring an application
            if _bu_type.lower( ) == "application":

                # get the account menu
                _app = _menu.app_menu( )

                # setup the repo path
                _repo_path = self.__repo_path( "application", _app[0], _app[1] )

                # setup the internal account and app
                self.account = _app[0]
                self.app = _app[1]

            # if we're restoring a database
            elif _bu_type.lower( ) == "database":

                # get the database
                _database = _menu.database_menu( )

                # setup the repo path
                _repo_path = self.__repo_path( "database", _database )

                # setup the database name
                self.database = _database

        # if we're browsing
        if _bu_method.lower( ) == "browse":

            # mount point input
            _mount_point = input( "Please type in a mount point path: [{}]".format( self.temp_mount_path ) ) or self.temp_mount_path

            # create the mount point if it doesn't exist
            self.common.execute( "mkdir -p {} && chmod -R 755 {}".format( _mount_point, _mount_point ) )

            # the command to run for mounting it
            _cmd = self.common.primary_command.format( "{} mount {}".format( _repo_path, _mount_point ) )
        
            # show a message
            self.common.my_print( "info", ( "*" * 52 ) )
            self.common.my_print( "info", "Your selected backup repo has been has been mounted to:" )
            self.common.my_print( "success", _mount_point )
            self.common.my_print( "info", "You must keep this open to utilize the mount point." )
            self.common.my_print( "info", "Please hold a few seconds for it to finish mounting." )
            self.common.my_print( "info", "Press CTRL-C to quit." )
            self.common.my_print( "info", ( "*" * 52 ) )

            # try to catch the exception
            try:

                # run the mount command
                self.common.execute( _cmd )       

            # catch the keyboard interrupt
            except KeyboardInterrupt:

                # show a message then exit
                self.common.my_print( "info", "\nYour mount point has been unmounted." )
                self.common.my_print( "info", ( "*" * 52 ) )
                sys.exit( )

        elif _bu_method.lower( ) == "manual":

            # now that we have the full repo path, present the menu of it's snapshots
            _snapshot = _menu.repo_menu( _repo_path )

            # have them type in the path they want to restore to
            _restore_path = input( "Please type in a restore path: [{}]".format( self.common.tmp_restore_location ) ) or self.common.tmp_restore_location

            # create the location directory if it is not already created
            self.common.execute( "mkdir -p {} && chmod -R 755 {}".format( _restore_path, _restore_path ) )

            # split out the id from the selected backup
            _id = _snapshot.split( "|" )

            # setup the restic command we need to run
            _cmd = self.common.primary_command.format( "{} restore {} --target {}".format( 
                _repo_path,
                _id[1], 
                _restore_path ) )

            # show a message to hold while restoring
            self.common.my_print( "info", ( "*" * 52 ) )
            self.common.my_print( "info", "Please hold while we run the restore." )
            self.common.my_print( "info", ( "*" * 52 ) )

            # execute the command
            self.common.execute( _cmd )

            self.common.my_print( "info", ( "*" * 52 ) )
            self.common.my_print( "success", "Your selected backup has been succesfully restored." )
            self.common.my_print( "info", ( "*" * 52 ) )

        elif _bu_method.lower( ) == "automatic":

            # now that we have the full repo path, present the menu of it's snapshots
            _snapshot = _menu.repo_menu( _repo_path )

            # split out the id from the selected backup
            _id = _snapshot.split( "|" )

            # if we're restoring a databasse
            if _bu_type.lower( ) == "database":

                # setup the command we need to run here
                _cmd = self.common.primary_command.format( "{}/ dump {} {}.sql | {}".format( 
                    _repo_path,
                    _id[1], 
                    self.database,
                    self.__mysql_command( ) + self.database ) )

            # otherwise it's an app
            else:

                # setup the restic command we need to run
                _cmd = self.common.primary_command.format( "{} restore {} --target {}".format( 
                    _repo_path,
                    _id[1], 
                    "/" ) )

            # show a message to hold while restoring
            self.common.my_print( "info", ( "*" * 52 ) )
            self.common.my_print( "info", "Please hold while we run the restore." )
            self.common.my_print( "info", ( "*" * 52 ) )

            # execute the command
            self.common.execute( _cmd )

            self.common.my_print( "info", ( "*" * 52 ) )
            self.common.my_print( "success", "Your selected backup has been succesfully restored." )
            self.common.my_print( "info", ( "*" * 52 ) )

        # remove the environment variables
        del os.environ['AWS_ACCESS_KEY_ID']
        del os.environ['AWS_SECRET_ACCESS_KEY']
        del os.environ['AWS_DEFAULT_REGION']
        del os.environ['RESTIC_PASSWORD']

    # create the repo path string
    def __repo_path( self, _type, _account = None, _application = None ):

        # if the backup type is an application
        if _type.lower( ) == "application":

            # set the repo path
            _repo_path = "{}{}/apps/{}/{}".format( "s3://{}/{}/".format( self.s3_endpoint, self.s3_bucket ), 
                self.bu_name, 
                _account, 
                _application )

        # the backup type is databases
        elif _type.lower( ) == "database":

            # set the repo path
            _repo_path = "{}{}/database/{}".format( "s3://{}/{}/".format( self.s3_endpoint, self.s3_bucket ), 
                self.bu_name, 
                _account )

        # the backup type is other
        elif _type.lower( ) == "other":

            # set the repo path
            _repo_path = "{}{}/other".format( "s3://{}/{}/".format( self.s3_endpoint, self.s3_bucket ), self.bu_name )

        return _repo_path

    # format the mysql command
    def __mysql_command( self ):

        # hold our command
        _cmd = self.get_mysql_binary( ) + " {} "

        # let's see if we have a defaults file
        if self.common.mysql_defaults:

            # we do, return the string with the defaults file appended
            return _cmd.format( "--defaults-file={}".format( self.common.mysql_defaults ) )
        
        # we don't, so test for a username and password
        elif ( self.common.mysql_user is not None ) and ( self.common.mysql_password is not None ):

            # we do, return the string with the user and password appended
            return _cmd.format( "-u {} -p{}".format( self.common.mysql_user, self.common.mysql_password ) )

        # we have nothing, so give it a shot.
        else:

            # return the string with no formatting
            return _cmd
            
    # get the right db binary
    def get_mysql_binary( self ):
    
        # Check for mariadb first (if you prefer it)
        if shutil.which('mariadb'):
            return 'mariadb'
        elif shutil.which('mysql'):
            return 'mysql'
        else:
            raise Exception("Neither mysql nor mariadb client found in PATH")
