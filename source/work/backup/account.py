#!/usr/bin/env python3

# common imports
import time, os, glob

# import the threadpool
from multiprocessing.pool import ThreadPool as Pool

class KP_Backup_Account:

    # initialize us
    def __init__( self, account, paths ):

        # we'll need our commmon class in here for some items, so import it now
        from work.common.common import KP_Common

        # let's set the class to a class wide variable so we can use it later on if we need
        self.common = KP_Common( )

        # hold the internal account
        self.account = account

        # hold the internal paths
        self.paths = paths

    # destroyer!
    def __del__( self ):

        # clean up
        del self.common, self.account, self.paths

    # run it
    def run( self ):

        # setup the backup path
        _path = "{}{}/{}/*".format( self.common.path_start, self.account, self.common.path_for_apps )

        # the true path
        _true_path = glob.glob( _path )

        # create our Threaded Pool
        _t_pool = Pool( self.common.allowed_threads )

        # loop the true path
        for p in _true_path:

            # add the backup to the pool
            _t_pool.apply_async( self.__run_account_backup, ( p, ) )

        # close up access to the pool
        _t_pool.close( )

        # join the threads to be run
        _t_pool.join( )

        # clean up
        del _t_pool

        # if paths exists
        if self.paths is not None:
            
            # process the "extra" path(s) backups
            self.common.run_other_backup( self.paths )

    # run the account backup
    def __run_account_backup( self, path ):

        # the apps name
        _app = os.path.basename( path )

        # the destination
        _dest = "{}{}/{}".format( self.common.backup_path_app, self.account, _app )

        # initialize if we need to
        self.common.backup_init( _dest )

        # run the backup
        self.common.backup_run( _dest, path )

        # clean up the backup
        self.common.backup_cleanup( _dest )