#!/usr/bin/env python3

# common imports
import gc, ctypes

class KP_Freem:

    # initialize us
    def __init__( self, _args = None ):

        # we'll need our commmon class in here for some items, so import it now
        from work.common.common import KP_Common

        # let's set the class to a class wide variable so we can use it later on if we need
        self.common = KP_Common( )

    # destroyer!
    def __del__( self ):

        # clean up the common
        del self.common


    # do what we need to do here
    def run( self ):

        # show a message
        print( "*" * 52 )
        self.common.my_print( "info", "Freeing up some system memory." )
        print( "*" * 52 )

        # drop our caches
        self.common.execute( "sync & echo 3 > /proc/sys/vm/drop_caches" )

        # do it again, incase that method did not work
        self.common.execute( "sync & sysctl -w vm.drop_caches=3" )

        # force the garbage collector to run
        gc.collect( )

        # try to release more memory
        _libc = ctypes.CDLL( "libc.so.6" )
        _libc.malloc_trim( 0 )

        print( "*" * 52 )
        self.common.my_print( "success", "All set." )
        print( "*" * 52 )

