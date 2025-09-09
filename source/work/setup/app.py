#!/usr/bin/env python3

# common imports
import time

class KP_App_Setup:

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

    # setup the apps necessary modules
    def setup_app( self ):

        # show a quick message
        self.common.my_print( "info", ( "*" * 52 ) )
        self.common.my_print( "success", "Please hold while we setup the apps necessities" )
        self.common.my_print( "info", ( "*" * 52 ) )

        # see if the apt module is installed, if not, install it
        try:

            # try to import it
            import apt
        except:

            # do it silently
            self.common.execute( 'apt-get install -y python3-apt' )

            # now that it's installed, import the module
            import apt
        
        # utilize the apt module
        _apt_cache = apt.Cache( )

        # try to update
        try:
            _apt_cache.update( )

        except:

            # for some reason, it failed, execute it normally
            self.common.execute( 'apt-get update' )

        # now open the cache
        _apt_cache.open( )

        # make sure boto3 is installed
        _boto3 = _apt_cache["python3-boto3"]
        if not _boto3.is_installed: 

            # it is not, flag it to be installed
            _boto3.mark_install( )

            # now attempt to comit the install
            try:
                _apt_cache.commit( )
            except:
                pass

        # hold restic
        _restic = _apt_cache["restic"]
        if not _restic.is_installed: 

            # it is not, flag it to be installed
            _restic.mark_install( )

            # now attempt to comit the install
            try:
                _apt_cache.commit( )
            except:
                pass

        # install pip if it is not currently installed
        _pip = _apt_cache['python3-pip']
        if not _pip.is_installed:

            # install it
            _pip.mark_install( )
            try:
                _apt_cache.commit( )
            except:
                pass

        # install python invoke, if it is not currently installed
        _invoke = _apt_cache['python3-invoke']
        if not _invoke.is_installed:

            # install it
            _invoke.mark_install( )
            try:
                _apt_cache.commit( )
            except:
                pass
        
        # check if the mysql python module is installed
        _mysql = _apt_cache['python3-mysqldb']
        if not _mysql.is_installed:

            # install it
            _mysql.mark_install( )
            try:
                _apt_cache.commit( )
            except:
                pass

        # make sure pip is up to date
        self.common.execute( 'pip3 install --user --upgrade pip --break-system-packages --root-user-action=ignore' )

        # we need dateutil module
        self.common.execute( 'pip3 install --upgrade python-dateutil --break-system-packages --root-user-action=ignore' )

        # we need the simple-term-me menu module
        self.common.execute( 'pip3 install --upgrade simple-term-menu --break-system-packages --root-user-action=ignore' )

        # close
        _apt_cache.close( )

        # sleep a little
        time.sleep( 5 )

        # show an "all set" message
        self.common.my_print( "info", ( "*" * 52 ) )
        self.common.my_print( "success", "The app is all set" )
        self.common.my_print( "info", ( "*" * 52 ) )
