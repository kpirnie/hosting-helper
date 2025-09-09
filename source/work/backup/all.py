#!/usr/bin/env python3

# common imports
import time, glob, os

# import the threadpool
from multiprocessing.pool import ThreadPool as Pool

class KP_Backup_All:

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

        # clean up
        del self.common, self.paths

    # run the backup
    def run( self ):

        # backup all databases first
        from work.backup.database import KP_Backup_Database

        # fireup the class
        _db = KP_Backup_Database( "all", self.paths )

        # run it
        _db.run( )

        # clean it up
        del _db

        # setup the path we're backing up here
        _path = "{}*/{}/*".format( self.common.path_start, self.common.path_for_apps )

        # get the true path we need to loop
        _true_path = glob.glob( _path )

        # create our Threaded Pool
        _t_pool = Pool( self.common.allowed_threads )

        # loop the true path
        for p in _true_path:

            # add the backup to the pool
            _t_pool.apply_async( self.__run_backup_paths, ( p, ) )

        # close up access to the pool
        _t_pool.close( )

        # join the threads to be run
        _t_pool.join( )

        # clean up
        del _t_pool

        # process the "extra" path(s) backups
        self.common.run_other_backup( self.paths )

    # backup all paths
    def __run_backup_paths( self, the_path ):

        # get the path ownership
        _acct = self.common.path_owner_user( the_path )

        # the apps name
        _app = os.path.basename( the_path )

        # the destination
        _dest = "{}{}/{}".format( self.common.backup_path_app, _acct, _app )

        # initialize if we need to
        self.common.backup_init( _dest )

        # run the backup
        self.common.backup_run( _dest, the_path )

        # clean up the backup
        self.common.backup_cleanup( _dest )
