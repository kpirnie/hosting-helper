#!/usr/bin/env python3

# common imports
import sys

class KP_Setup:

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
        del self.common

        # clean up parsed the arguments
        del self.parsed_args

        # clean up the arguments
        del self.args

    # do what we need to do here
    def run( self ):

        # make sure the setup argument exists
        if self.parsed_args.setup is None:

            # throw an error message here
            self.common.my_print( "info", ( "*" * 52 ) )
            self.common.my_print( "error", "You must pass the --setup argument [app|system]." )
            self.common.my_print( "info", ( "*" * 52 ) )
            sys.exit( )

        # if we are setting up the app
        if self.parsed_args.setup.lower( ) == "app":

            # import the setup class/module
            from work.setup.app import KP_App_Setup
            _app = KP_App_Setup( )

            # run the app setup
            _app.setup_app( )

            # clean up
            del _app

            # fire up the configurator
            from work.config.config import KP_Config

            # fire up the configurator class
            _config = KP_Config( )

            # run it
            _config.run( )

            # clean it up
            del _config
            
        # otherwise we are setting up the system
        elif self.parsed_args.setup.lower( ) == "system":

            # import the setup class/module
            from work.setup.system import KP_System_Setup
            _sys = KP_System_Setup( )

            # run the system setup
            _sys.setup_system( )

            # clean up
            del _sys
        