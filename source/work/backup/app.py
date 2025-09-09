#!/usr/bin/env python3

# common imports
import time

class KP_Backup_App:

    # initialize us
    def __init__( self, account, app, paths ):

        # we'll need our commmon class in here for some items, so import it now
        from work.common.common import KP_Common

        # let's set the class to a class wide variable so we can use it later on if we need
        self.common = KP_Common( )

        # hold the internal account
        self.account = account

        # hold the internal application
        self.application = app

        # hold the internal paths
        self.paths = paths

    # destroyer!
    def __del__( self ):

        # clean up
        del self.common, self.account, self.application, self.paths

    # run the backup
    def run( self ):

        # setup the backup path
        _path = "{}{}/{}/{}".format( self.common.path_start, self.account, self.common.path_for_apps, self.application )

        # setup the destination
        _dest = "{}{}/{}".format( self.common.backup_path_app, self.account, self.application )

        # initialize if we need to
        self.common.backup_init( _dest )

        # run the backup
        self.common.backup_run( _dest, _path )

        # clean up the backup
        self.common.backup_cleanup( _dest )

        # if paths exists
        if self.paths is not None:

            # process the "extra" path(s) backups
            self.common.run_other_backup( self.paths )
