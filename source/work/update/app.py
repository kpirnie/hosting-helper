#!/usr/bin/env python3

# common imports
import time

class KP_App_Update:

    # initialize us
    def __init__( self ):

        # we'll need our commmon class in here for some items, so import it now
        from work.common.common import KP_Common

        # let's set the class to a class wide variable so we can use it later on if we need
        self.common = KP_Common( )

        # 

    # destroyer!
    def __del__( self ):

        # clean up the common
        del self.common

    # update the app
    def update_app( self ):

        # show a quick message
        self.common.my_print( "info", ( "*" * 52 ) )
        self.common.my_print( "success", "Please hold while we update the apps necessities" )
        self.common.my_print( "info", ( "*" * 52 ) )

        # update the apps modules
        self._update_app_modules( )

        # now, check the releases and see if there is an updated version of the app itself
        

        # show an "all set" message
        self.common.my_print( "info", ( "*" * 52 ) )
        self.common.my_print( "success", "The app updates are all set" )
        self.common.my_print( "info", ( "*" * 52 ) )

    def __update_the_app( self ):

        print

    # update the modules the app needs
    def _update_app_modules( self ):

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

        # open up the apt cache
        _apt_cache.open( )

        # make sure boto3 is up to date
        _boto3 = _apt_cache["python3-boto3"]
        if _boto3.is_upgradable: 

            # it is, flag it to be upgraded
            _boto3.mark_upgrade( )

            # now attempt to comit the install
            try:
                _apt_cache.commit( )
            except:
                pass

        # hold restic
        _restic = _apt_cache["restic"]
        if _restic.is_upgradable: 

            # it is not, flag it to be installed
            _restic.mark_upgrade( )

            # now attempt to comit the install
            try:
                _apt_cache.commit( )
            except:
                pass

        # install pip if it is not currently installed
        _pip = _apt_cache['python3-pip']
        if _pip.is_upgradable:

            # install it
            _pip.mark_upgrade( )
            try:
                _apt_cache.commit( )
            except:
                pass

        # install python invoke, if it is not currently installed
        _invoke = _apt_cache['python3-invoke']
        if _invoke.is_upgradable:

            # install it
            _invoke.mark_upgrade( )
            try:
                _apt_cache.commit( )
            except:
                pass
        
        # check if the mysql python module is installed
        _mysql = _apt_cache['python3-mysqldb']
        if _mysql.is_upgradable:

            # install it
            _mysql.mark_upgrade( )
            try:
                _apt_cache.commit( )
            except:
                pass
                
        # make sure pip is up to date
        self.common.execute( 'python -m pip install --user --upgrade pip --break-system-packages --root-user-action=ignore' )

        # we need dateutil module
        self.common.execute( 'python -m pip install --upgrade python-dateutil --break-system-packages --root-user-action=ignore' )

        # we need the simple-term-menu module
        self.common.execute( 'python -m pip install --upgrade simple-term-menu --break-system-packages --root-user-action=ignore' )

        # close
        _apt_cache.close( )
