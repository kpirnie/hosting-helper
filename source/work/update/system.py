#!/usr/bin/env python3

# common imports
import time, os, shutil

class KP_System_Update:

    # initialize us
    def __init__( self ):

        # we'll need our commmon class in here for some items, so import it now
        from work.common.common import KP_Common

        # let's set the class to a class wide variable so we can use it later on if we need
        self.common = KP_Common( )

    # destroyer!
    def __del__( self ):

        # clean up the common
        del self.common

    # run the system updaters
    def update_system( self ):

        # show a quick message
        self.common.my_print( "info", ( "*" * 52 ) )
        self.common.my_print( "success", "Please hold while we update the system" )
        self.common.my_print( "info", ( "*" * 52 ) )

        # update and upgrade maldet
        self.common.execute( "maldet -u" )
        self.common.execute( "maldet -d" )

        # since we've only install clamav on systems with 2G or greater, check and make sure it's actually installed before attempting to update it
        if shutil.which( "freshclam" ) is not None:

            # update clamav
            self.common.execute( "freshclam" )

        # update wp-cli
        self.common.execute( "wp --allow-root cli update" )

        # update apt's cache
        self.common.execute( "apt-get update" )

        # run the apt upgrade
        self.common.execute( "apt-get -y upgrade" )

        # now autoremove
        self.common.execute( "apt-get -y autoremove" )

        # now autoclean
        self.common.execute( "apt-get autoclean" )

        # sleep a little
        time.sleep( 5 )

        # show an "all set" message
        self.common.my_print( "info", ( "*" * 52 ) )
        self.common.my_print( "success", "The system is all set and updated" )

        # check if the server needs to be restarted
        if os.path.exists( "/var/run/reboot-required" ):

            # it does, so notify them
            self.common.my_print( "success", "Please note, your system needs to be rebooted." )

        self.common.my_print( "info", ( "*" * 52 ) )
