#!/usr/bin/env python3

# common imports
import sys, os

class KP_Backup:

    # initialize us
    def __init__( self, _args = None ):

        # we'll need our commmon class in here for some items, so import it now
        from work.common.common import KP_Common

        # let's set the class to a class wide variable so we can use it later on if we need
        self.common = KP_Common( )

        # hold the arguments
        self.args = _args

        # hold the parsed arguments
        self.parsed_args = _args.parse_args( )

    # destroyer!
    def __del__( self ):

        # clean up the common
        del self.common, self.parsed_args, self.args

    # do what we need to do here
    def run( self ):

        # make sure the backup argument exists
        if self.parsed_args.backup is None:

            # throw an error message here
            self.common.my_print( "info", ( "*" * 52 ) )
            self.common.my_print( "error", "You must pass the --backup argument [account|acct|application|app|database|db|other|all]" )
            self.common.my_print( "info", ( "*" * 52 ) )
            sys.exit( )

        # hold the paths argument if it was passed
        _paths = self.parsed_args.paths or None

        # set some environment variables
        os.environ["AWS_ACCESS_KEY_ID"] = self.common.key
        os.environ["AWS_SECRET_ACCESS_KEY"] = self.common.secret
        os.environ["AWS_DEFAULT_REGION"] = self.common.region
        os.environ["RESTIC_PASSWORD"] = self.common.hash

        # if we are backing up everything!
        if self.parsed_args.backup.lower( ) == "all":

            # message
            self.common.my_print( "info", ( "*" * 52 ) )
            self.common.my_print( "success", "Starting to backup everything." )
            self.common.my_print( "info", ( "*" * 52 ) )

            # import the all module
            from work.backup.all import KP_Backup_All

            # fireup the class
            _all = KP_Backup_All( _paths )

            # run it
            _all.run( )

            # clean it up
            del _all

            # completion message
            self.common.my_print( "info", ( "*" * 52 ) )
            self.common.my_print( "success", "Your backup has completed." )
            self.common.my_print( "info", ( "*" * 52 ) )
            sys.exit( )

        # if we are backing up an account
        elif self.parsed_args.backup.lower( ) in [ "acct", "account" ]:

            # check if the account arg has been passed or not
            if self.parsed_args.account is None:

                # we need an account specified
                _acct = input( "Please type the account you wish to backup: [null]" ) or None

            # otherwise it has
            else:

                _acct = self.parsed_args.account

            # if the account is none, throw an error message and exist
            if _acct is None:

                self.common.my_print( "info", ( "*" * 52 ) )
                self.common.my_print( "error", "You must specify the account you wish to backup." )
                self.common.my_print( "info", ( "*" * 52 ) )
                sys.exit( )

            # otherwise we can proceed
            else:

                # message
                self.common.my_print( "info", ( "*" * 52 ) )
                self.common.my_print( "success", "Starting your backup of account: {}".format( _acct ) )
                self.common.my_print( "info", ( "*" * 52 ) )

                # import the account backup
                from work.backup.account import KP_Backup_Account

                # fire up the class
                _acct_bu = KP_Backup_Account( _acct, _paths )

                # run the backup
                _acct_bu.run( )

                # clean up
                del _acct_bu

                # completion message
                self.common.my_print( "info", ( "*" * 52 ) )
                self.common.my_print( "success", "Your backup has completed." )
                self.common.my_print( "info", ( "*" * 52 ) )
                sys.exit( )

        # elseif we're backing up an app
        elif self.parsed_args.backup.lower( ) in [ "app", "application" ]:

            # check if the account arg has been passed or not
            if self.parsed_args.account is None:

                # we need an account specified
                _acct = input( "Please type the account you wish to backup: [null]" ) or None

            # otherwise it has
            else:

                _acct = self.parsed_args.account

            # check if the application arg has been passed or not
            if self.parsed_args.application is None:

                # we need an account specified
                _app = input( "Please type the application you wish to backup: [null]" ) or None

            # otherwise it has
            else:

                _app = self.parsed_args.application

            # if the account or app is none, throw an error message and exist
            if None in ( _acct, _app ):

                self.common.my_print( "info", ( "*" * 52 ) )
                self.common.my_print( "error", "You must specify the account and the application you wish to backup." )
                self.common.my_print( "info", ( "*" * 52 ) )
                sys.exit( )

            # otherwise we can proceed
            else:

                # message
                self.common.my_print( "info", ( "*" * 52 ) )
                self.common.my_print( "success", "Starting your backup of accounts '{}' app: '{}'".format( _acct, _app ) )
                self.common.my_print( "info", ( "*" * 52 ) )

                # import the app backup
                from work.backup.app import KP_Backup_App

                # fire up the class
                _app_bu = KP_Backup_App( _acct, _app, _paths )

                # run the backup
                _app_bu.run( )

                # clean up
                del _app_bu

                # completion message
                self.common.my_print( "info", ( "*" * 52 ) )
                self.common.my_print( "success", "Your backup has completed." )
                self.common.my_print( "info", ( "*" * 52 ) )
                sys.exit( )

        # elseif we're backing up a database
        elif self.parsed_args.backup.lower( ) in [ "db", "database" ]:

            # check if the database arg has been passed or not
            if self.parsed_args.database is None:

                # we need an database specified
                _db = input( "Please type the database you wish to backup, or ALL: [null]" ) or None

            # otherwise it has
            else:

                _db = self.parsed_args.database

            # if the database is none, throw an error message and exist
            if _db is None:

                self.common.my_print( "info", ( "*" * 52 ) )
                self.common.my_print( "error", "You must specify the database you wish to backup." )
                self.common.my_print( "info", ( "*" * 52 ) )
                sys.exit( )

            # otherwise we can proceed
            else:

                # message
                self.common.my_print( "info", ( "*" * 52 ) )
                self.common.my_print( "success", "Starting your database backup." )
                self.common.my_print( "info", ( "*" * 52 ) )

                # import the database backup
                from work.backup.database import KP_Backup_Database

                # fire up the class
                _dbc = KP_Backup_Database( _db, _paths )

                # run the backup
                _dbc.run( )

                # clean it up
                del _dbc

                # completion message
                self.common.my_print( "info", ( "*" * 52 ) )
                self.common.my_print( "success", "Your backup has completed." )
                self.common.my_print( "info", ( "*" * 52 ) )
                sys.exit( )

        # elseif we're backing up something else
        elif self.parsed_args.backup.lower( ) == "other":

            # if the paths are not specified, ask for them
            if _paths is None:

                _paths = input( "Please type in the comma-delimited list of paths you would like to backup: [null]" ) or None

            # if the paths is still none, throw an error message and exist
            if _paths is None:

                self.common.my_print( "info", ( "*" * 52 ) )
                self.common.my_print( "error", "You must specify the paths you wish to backup." )
                self.common.my_print( "info", ( "*" * 52 ) )
                sys.exit( )

            # otherwise we can proceed
            else:

                # message
                self.common.my_print( "info", ( "*" * 52 ) )
                self.common.my_print( "success", "Starting your backup." )
                self.common.my_print( "info", ( "*" * 52 ) )

                # run the common other backup
                self.common.run_other_backup( _paths )

                # completion message
                self.common.my_print( "info", ( "*" * 52 ) )
                self.common.my_print( "success", "Your backup has completed." )
                self.common.my_print( "info", ( "*" * 52 ) )
                sys.exit( )

        # remove the environment variables
        del os.environ['AWS_ACCESS_KEY_ID']
        del os.environ['AWS_SECRET_ACCESS_KEY']
        del os.environ['AWS_DEFAULT_REGION']
        del os.environ['RESTIC_PASSWORD']
