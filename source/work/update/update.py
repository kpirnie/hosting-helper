#!/usr/bin/env python3

# common imports
import sys

class KP_Update:

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

        # make sure the update argument exists
        if self.parsed_args.update is None:

            # throw an error message here
            self.common.my_print( "info", ( "*" * 52 ) )
            self.common.my_print( "error", "You must pass the --update argument [wordpress]." )
            self.common.my_print( "info", ( "*" * 52 ) )
            sys.exit( )

        # we are updating wordpress
        if self.parsed_args.update.lower( ) == "wordpress":

            # import the class/module
            from work.update.wordpress import KP_Wordpress_Update

            # fire up the class
            _wp = KP_Wordpress_Update( )

            # run the updates
            _wp.update_wordpress( self.parsed_args.include_plugins or False )

            # clean up
            del _wp