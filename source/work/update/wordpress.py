#!/usr/bin/env python3

# common imports
import os, time, sys, requests, glob
from urllib3.exceptions import InsecureRequestWarning

# import the threadpool
from multiprocessing.pool import ThreadPool as Pool

# wordpress updates class
class KP_Wordpress_Update:

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

    # update wordpress
    def update_wordpress( self, include_plugins = False ):
        
        # show a message that it's starting
        self.common.my_print( "info", ( "*" * 52 ) )
        self.common.my_print( "success", "Please hold while we backup\nand update your Wordpress installs." )
        self.common.my_print( "info", ( "*" * 52 ) )

        # set the path list
        _path_list = os.scandir( self.common.path_start )

        # loop over the starting path
        for _dir in _path_list:

            # only do this for directories
            if _dir.is_dir( ):
                
                # the app path
                _app_path = "{}/{}/".format( _dir.path, self.common.path_for_apps )
                
                # make sure backup_apps_name actually exists before proceeding
                if os.path.exists( _app_path ):

                    _path_list = os.scandir( _app_path )

                    # create our Threaded Pool
                    _t_pool = Pool( self.common.allowed_threads )

                    # find all the apps
                    for _wa in _path_list:

                        # add the updates to the pool
                        _t_pool.apply_async( self.__run_updates, ( _wa, include_plugins, ) )

                    # close up access to the pool
                    _t_pool.close( )

                    # join the threads to be run
                    _t_pool.join( )

                    # clean up
                    del _t_pool

        # end message
        self.common.my_print( "info", ( "*" * 52 ) )
        self.common.my_print( "success", "Your Wordpress installs have been updated.\nPlease note you may need to clear your caches." )
        self.common.my_print( "info", ( "*" * 52 ) )
    
    # the update method for our threaded loop above
    def __run_updates( self, _path, include_plugins ):

        # possible wordpress path
        _wp_path = "{}/wp-config.php".format( _path.path )

        # check if we're a wordpress install in this directory
        if os.path.exists( _wp_path ):

            # get the account
            _acct = self.common.path_owner_user( _path.path )

            # the actual app
            _app = os.path.basename( _path.path )

            # get the sites URL
            _site_url_cmd = "wp --allow-root option get siteurl --path={}/".format( _path.path )

            # check and return the sites URL for testing later on
            _site_url = self.common.execute( _site_url_cmd, False )
            _site_url = _site_url.decode( "utf-8" ).replace( '\n', '' )

            # get the apps database name
            _db_name_cmd = "wp --allow-root eval 'echo DB_NAME;' --path={}/".format( _path.path )
            _db_name = self.common.execute( _db_name_cmd, False )
            _db_name = _db_name.decode( "utf-8" )

            # backup the app and the database for it
            self.__backup( _acct, _app, _db_name )

            # run the core updates                        
            _core_cmd = "wp --allow-root core update --path={}/".format( _path.path )
            _core_db_upgrade = "wp --allow-root core update-db --path={}/".format( _path.path )
            
            # run the commands
            self.common.execute( _core_cmd )
            self.common.execute( _core_db_upgrade )

            # make sure we reset the permissions here
            self.common.execute( "chown -R {}:{} {}".format( _acct, _acct, _path.path ) )

            # test the site
            _core_test = self.__test_response( _site_url )

            # if the core test fails, restore the app, show a message, then dump out of the loop for this app
            if not _core_test:

                # restore the app
                self.__restore( _acct, _app, _db_name )

                self.common.my_print( "info", ( "*" * 52 ) )
                self.common.my_print( "error", "Wordpress Core updates have failed and the app has been restored." )
                self.common.my_print( "error", "Please check your server error logs." )
                self.common.my_print( "info", ( "*" * 52 ) )

                # break out of this iteration.  core failed, so do not bother with plugins
                return

            # otherwise it succeeded
            else:

                # optimize the database
                _db_optimize = "wp --allow-root db optimize --path={}/".format( _path.path )

                # run the command
                self.common.execute( _db_optimize )
                
            # if we're also updating plugins
            if include_plugins:

                # backup the app and the database for it
                self.__backup( _acct, _app, _db_name )

                _plugin_cmd = "wp --allow-root plugin update --all --path={}/".format( _path.path )
                _theme_cmd = "wp --allow-root theme update --all --path={}/".format( _path.path )

                # run the commands
                self.common.execute( _plugin_cmd )
                self.common.execute( _theme_cmd )

                # make sure we reset the permissions here
                self.common.execute( "chown -R {}:{} {}".format( _acct, _acct, _path.path ) )

                # test for validity
                _plugin_test = self.__test_response( _site_url )

                # if the plugin test fails, restore the app, show a message, then dump out of the loop for this app
                if not _plugin_test:

                    # restore the app
                    self.__restore( _acct, _app, _db_name )

                    self.common.my_print( "info", ( "*" * 52 ) )
                    self.common.my_print( "error", "Wordpress Plugin updates have failed and the app has been restored." )
                    self.common.my_print( "error", "Please check your server error logs." )
                    self.common.my_print( "info", ( "*" * 52 ) )

                    # break out of this iteration.  core failed, so do not bother with plugins
                    return

    # test the site for at least a 200 response code
    def __test_response( self, _url ):

        # setup the request headers
        _headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:17.0) Gecko/20100101 Firefox/17.0' }

        # supress the cert warnings
        requests.packages.urllib3.disable_warnings( category=InsecureRequestWarning )

        # setup the request session
        with requests.Session( ) as _request:

            # let's try
            try:
                # perform the actual request
                _resp = _request.get( _url, headers=_headers, allow_redirects=True, verify=False )

                # hold the status code
                _s_code = _resp.status_code
            except:

                # set the status code to 500
                _s_code = 500

            # if we do have a valid response code
            if _s_code == 200:
                
                # return true
                return True

        # default return false
        return False

    # backup the app and database
    def __backup( self, _acct, _app, _db ):

        # set some environment variables
        os.environ["AWS_ACCESS_KEY_ID"] = self.common.key
        os.environ["AWS_SECRET_ACCESS_KEY"] = self.common.secret
        os.environ["AWS_DEFAULT_REGION"] = self.common.region
        os.environ["RESTIC_PASSWORD"] = self.common.hash
        
        # import the database backup
        from work.backup.database import KP_Backup_Database

        # fire up the class
        _dbc = KP_Backup_Database( _db, None )

        # run the backup
        _dbc.run( )

        # clean it up
        del _dbc

        # import the app backup
        from work.backup.app import KP_Backup_App

        # fire up the class
        _app_bu = KP_Backup_App( _acct, _app, None )

        # run the backup
        _app_bu.run( )

        # clean up
        del _app_bu

        # remove the environment variables
        del os.environ['AWS_ACCESS_KEY_ID']
        del os.environ['AWS_SECRET_ACCESS_KEY']
        del os.environ['AWS_DEFAULT_REGION']
        del os.environ['RESTIC_PASSWORD']

    # restore the app and database
    def __restore( self, account, application, database ):

        # set some environment variables
        os.environ["AWS_ACCESS_KEY_ID"] = self.common.key
        os.environ["AWS_SECRET_ACCESS_KEY"] = self.common.secret
        os.environ["AWS_DEFAULT_REGION"] = self.common.region
        os.environ["RESTIC_PASSWORD"] = self.common.hash

        # setup the database repo path
        _db_repo = "{}{}/database/{}".format( "s3://{}/{}/".format( self.common.endpoint, self.common.bucket ), 
                self.common.name, 
                database )

        # setup the app repo
        _app_repo = "{}{}/apps/{}/{}".format( "s3://{}/{}/".format( self.common.endpoint, self.common.bucket ), 
                self.common.name, 
                account, 
                application )

        # setup the command we need to run here for the database restore
        _db_restore_cmd = self.common.primary_command.format( "{}/ dump {} {}.sql | {}".format( 
            _db_repo,
            "latest", 
            database,
            self.__mysql_command( ) + database ) )

        # setup the command we need to run here for the app restore
        _app_restore_cmd = self.common.primary_command.format( "{} restore {} --target {}".format( 
            _app_repo,
            "latest", 
            "/" ) )

        # execute the database restore
        self.common.execute( _db_restore_cmd )

        # execute the app restore
        self.common.execute( _app_restore_cmd )

        # remove the environment variables
        del os.environ['AWS_ACCESS_KEY_ID']
        del os.environ['AWS_SECRET_ACCESS_KEY']
        del os.environ['AWS_DEFAULT_REGION']
        del os.environ['RESTIC_PASSWORD']

    # format the mysql command
    def __mysql_command( self ):

        # hold our command
        _cmd = "mysql {} "

        # let's see if we have a defaults file
        if self.common.mysql_defaults:

            # we do, return the string with the defaults file appended
            return _cmd.format( "--defaults-file={}".format( self.common.mysql_defaults ) )
        
        # we don't, so test for a username and password
        elif ( self.common.mysql_user is not None ) and ( self.common.mysql_password is not None ):

            # we do, return the string with the user and password appended
            return _cmd.format( "-u {} -p{}".format( self.common.mysql_user, self.common.mysql_password ) )

        # we have nothing, so give it a shot.
        else:

            # return the string with no formatting
            return _cmd
            