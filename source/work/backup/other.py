#!/usr/bin/env python3

# common imports
import time, os

# import the threadpool
from multiprocessing.pool import ThreadPool as Pool

class KP_Backup_Other:

    # initialize us
    def __init__( self, paths ):

        # we'll need our commmon class in here for some items, so import it now
        from work.common.common import KP_Common

        # let's set the class to a class wide variable so we can use it later on if we need
        self.common = KP_Common( )

        # hold the internal paths
        self.paths = paths

    # destroyer!
    def __del__( self ):

        # clean up the common
        del self.common, self.paths

    # run the backup
    def run( self ):

        # make sure there are actually paths
        if self.paths:

            # split the paths string on the comma
            _the_paths = self.paths.replace( " ", "" ).strip( ).split( "," )

            # create our Threaded Pool
            _t_pool = Pool( self.common.allowed_threads )

            # loop over the resulting list
            for _path in _the_paths:

                # add the backup to the pool
                _t_pool.apply_async( self.__backup_other, ( _path, ) )

            # close up access to the pool
            _t_pool.close( )

            # join the threads to be run
            _t_pool.join( )

            # clean up
            del _t_pool

    # backup other
    def __backup_other( self, the_path ):

        # setup the absolute path
        _abs_path = os.path.expanduser( the_path )

        # the destination
        _dest = "{}{}".format( self.common.backup_path_other, _abs_path )

        # initialize if we need to
        self.common.backup_init( _dest )

        # run the backup
        self.common.backup_run( _dest, _abs_path )

        # clean up the backup
        self.common.backup_cleanup( _dest )
