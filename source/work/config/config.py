#!/usr/bin/env python3

# common imports
import sys, time, os, json, random, string, getpass, stat

class KP_Config:

    # initialize us
    def __init__( self, _args = None ):

        # we'll need our commmon class in here for some items, so import it now
        from work.common.common import KP_Common

        # let's set the class to a class wide variable so we can use it later on if we need
        self.common = KP_Common( )

        # hold the arguments
        self.args = _args

        # if there are arguments
        if _args is not None:

            # hold the parsed arguments
            self.parsed_args = _args.parse_args( )

    # destroyer!
    def __del__( self ):

        # clean up the common
        del self.common
        
        # if there are arguments
        if self.args is not None:

            del self.parsed_args, self.args

    # do what we need to do here
    def run( self ):

        # default to overwrite the config?
        _overwrite = False
        
        # prompt to choose to overwrite or not
        if os.path.exists( self.common.config_file ):

            # notify them that it already exists
            print( "*" * 52 )
            self.common.my_print( "info", "Your app is already configured." )
            _reconfig = input( "Do you want to re-configure it? [y/N] " ) or 'n'
            print( "*" * 52 )

            # the user wants to reconfigure so set the flag
            if _reconfig.lower( ) == "y":

                # yup!
                _overwrite = True
            else:

                print( "*" * 52 )
                self.common.my_print( "info", "You have chosen not to re-configure." )
                print( "*" * 52 )
                sys.exit( )

        # it hasn't been configured yet, so we can safely set this flag to True
        else:
            _overwrite = True

        # if we are overwriting
        if _overwrite:

            print( "*" * 52 )
            self.common.my_print( "info", "We need to ask for some information." )
            self.common.my_print( "info", "Please make sure you pay attention." )
            print( "*" * 52 )
            time.sleep( 5 )

            # generate a random password between 32 and 64 characters long
            _rand_pw = "" . join( random.choice( string.ascii_letters + string.digits ) for i in range( random.randint( 32, 64 ) ) )

            # how many days worth of backups should be kept
            _bu_retention = input( "How may days should backups be retained: [30] " ) or 30

            # user supplied encryption key
            _enc_key = getpass.getpass( "Enter an encryption key to use: [random] " ) or _rand_pw

            # aws key
            _key = getpass.getpass( "Enter your S3 API Key: " )

            # aws secret
            _secret = getpass.getpass( "Enter your S3 API Secret: " )

            # S3 Endpoint
            _s3_endpoint = input( "Enter your S3 Endpoint: [s3.amazonaws.com]" ) or "s3.amazonaws.com"

            # S3 Bucket
            _s3_bucket = input( "Enter your S3 Bucket: " ) or None

            # S3 Region
            _s3_region = input( "Enter the S3 region: [us-east-1]" ) or "us-east-1"

            # backup name, default to machine's hostname
            _backup_name = input( "Enter a name for the backup: [{}] ".format( self.common.hostname ) ) or self.common.hostname

            # Starting path
            _start_path = input( "Backup starting path: [/home/]" ) or "/home/"

            # Application path
            _apps_name = input( "Backup applications name: [webapps]" ) or "webapps"

            # mysql host
            _mysql_host = input( "Enter your mysql host server: [localhost]" ) or "localhost"

            # mysql defaults path
            _mysql_defaults = input( "Enter your mysql defaults file path (if left empty, you will be prompted for the admin user and password): [null]" ) or None

            # default mysql username and password = None
            _mysql_un = None
            _mysql_pw = None

            # check if the mysql defaults path was empty
            if not _mysql_defaults:

                # mysql username
                _mysql_un = input( "Enter your mysql admin username: [null] " ) or None
                    
                # mysql password
                _mysql_pw = getpass.getpass( "Enter your mysql admin password:  [null] " ) or None

            # make sure we have a key, secret, and bucket, if not let them know, then exit
            if ( not _key ) or ( not _secret ) or ( not _s3_bucket ):

                # throw an error message and exit
                print( "*" * 52 )
                self.common.my_print( "error", "You cannot backup unless you input your API Key, your API Secret, and your Bucket." )
                self.common.my_print( "error", "Please get this information, and try again." )
                print( "*" * 52 )
                sys.exit( )

            else:

                # if there wasn't an encryption key entered, generate one, and display it 
                if _enc_key == "":

                    # show the message
                    print( "*" * 52 )
                    self.common.my_print( "info", "You did not type in an encryption key\nOne has been generated for you.\nPlease make note of it now, you will need it to restore on another machine:\n{}".format( _rand_pw ) )
                    print( "*" * 52 )
                    _enc_key = _rand_pw

                # show a message if mysql admin credentials are NOT entered
                if ( _mysql_defaults == "" ) or ( _mysql_un == "" ) or ( _mysql_pw == "" ):

                    # show a message
                    print( "*" * 52 )
                    self.common.my_print( "info", "You did not type in a mysql admin user or password.\nAs a result, we may not be able to backup your databases." )
                    print( "*" * 52 )

                # check if the config file already exists
                if os.path.exists( self.common.config_file ):

                    # it does, so remove it first
                    os.remove( self.common.config_file )

                # hold a dict object to populate for our settings
                _settings = []

                # append the settings to the dictionary
                _settings.append( {
                    "key" : _key,
                    "secret" : _secret,
                    "hash" : _enc_key,
                    "endpoint" : _s3_endpoint,
                    "bucket" : _s3_bucket,
                    "region" : _s3_region,
                    "retention" : int( _bu_retention ),
                    "name" : _backup_name,
                    "path_start" : _start_path,
                    "path_for_apps" : _apps_name,
                    "mysql_host" : _mysql_host,
                    "mysql_defaults" : _mysql_defaults,
                    "mysql_user" : _mysql_un,
                    "mysql_password" : _mysql_pw
                } )

                # create our config file, and write in the json string
                with open( self.common.config_file, 'w' ) as _out_file:

                    # dump the json into it
                    json.dump( _settings, _out_file )

                # now we only want 600 permissions on this file
                os.chmod( self.common.config_file, stat.S_IRUSR )

                print( "*" * 52 )
                self.common.my_print( "success", "Your configuration has been written. You can now proceed with your backups" )
                print( "*" * 52 )
                sys.exit( )