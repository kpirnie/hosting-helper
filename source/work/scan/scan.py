#!/usr/bin/env python3

# common imports
import os, sys, glob

# import the threadpool
from multiprocessing.pool import ThreadPool as Pool

class KP_Scan:

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
        del self.common, self.args, self.parsed_args


    # do what we need to do here
    def run( self ):
        
        # make sure the scan argument exists
        if self.parsed_args.scan is None:

            # throw an error message here
            self.common.my_print( "info", ( "*" * 52 ) )
            self.common.my_print( "error", "You must pass the --scan argument [account|acct|application|app|other|all]" )
            self.common.my_print( "info", ( "*" * 52 ) )
            sys.exit( )

        # hold the paths argument if it was passed
        _paths = self.parsed_args.paths or None

        # if we are scanning everything
        if self.parsed_args.scan.lower( ) == "all":

            # message
            self.common.my_print( "info", ( "*" * 52 ) )
            self.common.my_print( "success", "Starting the scanner." )
            self.common.my_print( "info", ( "*" * 52 ) )

            # run the scan over the path
            _path = "{}?/{}/?".format( self.common.path_start, self.common.path_for_apps )

            # run the actual scan
            self.__scan( _path )

            # message
            self.common.my_print( "info", ( "*" * 52 ) )
            self.common.my_print( "success", "Good to go." )
            self.common.my_print( "info", ( "*" * 52 ) )

        # elseif we are scanning an account
        elif self.parsed_args.scan.lower( ) in [ "account", "acct" ]:

            # check if the account arg has been passed or not
            if self.parsed_args.account is None:

                # we need an account specified
                _acct = input( "Please type the account you wish to scan: [null]" ) or None

            # otherwise it has
            else:

                _acct = self.parsed_args.account

            # if the account is none, throw an error message and exist
            if _acct is None:

                self.common.my_print( "info", ( "*" * 52 ) )
                self.common.my_print( "error", "You must specify the account you wish to scan." )
                self.common.my_print( "info", ( "*" * 52 ) )
                sys.exit( )

            else:

                # message
                self.common.my_print( "info", ( "*" * 52 ) )
                self.common.my_print( "success", "Starting the scanner." )
                self.common.my_print( "info", ( "*" * 52 ) )

                # get the path to the account
                _path = "{}{}/{}/?".format( self.common.path_start, _acct, self.common.path_for_apps )

                # run the actual scan
                self.__scan( _path )

                # message
                self.common.my_print( "info", ( "*" * 52 ) )
                self.common.my_print( "success", "Good to go." )
                self.common.my_print( "info", ( "*" * 52 ) )

        # elseif we are optimizing an app
        elif self.parsed_args.scan.lower( ) in [ "application", "app" ]:

            # check if the account arg has been passed or not
            if self.parsed_args.account is None:

                # we need an account specified
                _acct = input( "Please type the account you wish to scan: [null]" ) or None

            # otherwise it has
            else:

                _acct = self.parsed_args.account

            # check if the application arg has been passed or not
            if self.parsed_args.application is None:

                # we need an account specified
                _app = input( "Please type the application you wish to scan: [null]" ) or None

            # otherwise it has
            else:

                _app = self.parsed_args.application

            # if the account or app is none, throw an error message and exist
            if None in ( _acct, _app ):

                self.common.my_print( "info", ( "*" * 52 ) )
                self.common.my_print( "error", "You must specify the account and the application you wish to scan." )
                self.common.my_print( "info", ( "*" * 52 ) )
                sys.exit( )

            # otherwise we can proceed
            else:

                # message
                self.common.my_print( "info", ( "*" * 52 ) )
                self.common.my_print( "success", "Starting the scanner." )
                self.common.my_print( "info", ( "*" * 52 ) )

                # get the path to the accounts app
                _path = "{}{}/{}/{}".format( self.common.path_start, _acct, self.common.path_for_apps, _app )

                # run the scan
                self.__scan( _path )

                # message
                self.common.my_print( "info", ( "*" * 52 ) )
                self.common.my_print( "success", "Good to go." )
                self.common.my_print( "info", ( "*" * 52 ) )

        # elseif we are scanning something else
        elif self.parsed_args.scan.lower( ) == "other":

            # if the paths are not specified, ask for them
            if _paths is None:

                _paths = input( "Please type in the comma-delimited list of paths you would like to scan: [null]" ) or None

            # if the paths is still none, throw an error message and exist
            if _paths is None:

                self.common.my_print( "info", ( "*" * 52 ) )
                self.common.my_print( "error", "You must specify the paths you wish to scan." )
                self.common.my_print( "info", ( "*" * 52 ) )
                sys.exit( )

            # otherwise we can proceed
            else:

                # message
                self.common.my_print( "info", ( "*" * 52 ) )
                self.common.my_print( "success", "Starting the scanner." )
                self.common.my_print( "info", ( "*" * 52 ) )

                # get the paths we want to optimize
                _the_paths = _paths.replace( " ", "" ).strip( ).split( "," )

                # create our Threaded Pool
                _t_pool = Pool( self.common.allowed_threads )

                for p in _the_paths:

                    # add the backup to the pool
                    _t_pool.apply_async( self.__scan, ( p, ) )

                # close up access to the pool
                _t_pool.close( )

                # join the threads to be run
                _t_pool.join( )

                # clean up
                del _t_pool

                # message
                self.common.my_print( "info", ( "*" * 52 ) )
                self.common.my_print( "success", "Good to go." )
                self.common.my_print( "info", ( "*" * 52 ) )

    # do the actual scanning
    def __scan( self, path ):

        # run the scan and return the output
        _ret = self.common.execute( "maldet -a {}".format( path ), False ).decode( )

        print(_ret)

        # get just the ID string
        _scanid = _ret.split( "--report" )[1]

        # check if we need to quarantine the hits
        if self.parsed_args.auto_quarantine:

            # we do, so quarantine the hits from the scanid
            self.common.execute( "maldet -q {}".format( _scanid.strip( ) ) )

        # check if we need to clean the hits
        if self.parsed_args.auto_clean:

            # we do, so clean the hits from the scanid
            self.common.execute( "maldet -n {}".format( _scanid.strip( ) ) )
