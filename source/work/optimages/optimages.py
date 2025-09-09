#!/usr/bin/env python3

# common imports
import os, sys, glob

# import the threadpool
from multiprocessing.pool import ThreadPool as Pool

class KP_Optimages:

    # initialize us
    def __init__( self, _args = None ):

        # we'll need our commmon class in here for some items, so import it now
        from work.common.common import KP_Common

        # let's set the class to a class wide variable so we can use it later on if we need
        self.common = KP_Common( )

        # hold the arguments
        self.args = _args

        # hold the parsed arguments
        self.parsed_args = _args.parse_args( )

    # destroyer!
    def __del__( self ):

        # clean up the common
        del self.common, self.args, self.parsed_args


    # do what we need to do here
    def run( self ):

        # make sure the optimize argument exists
        if self.parsed_args.optimize is None:

            # throw an error message here
            self.common.my_print( "info", ( "*" * 52 ) )
            self.common.my_print( "error", "You must pass the --optimize argument [account|acct|application|app|other|all]" )
            self.common.my_print( "info", ( "*" * 52 ) )
            sys.exit( )

        # hold the paths argument if it was passed
        _paths = self.parsed_args.paths or None

        # if we are optimizing everything
        if self.parsed_args.optimize.lower( ) == "all":

            self.common.my_print( "info", ( "*" * 52 ) )
            self.common.my_print( "success", "Starting the image processor." )
            self.common.my_print( "info", ( "*" * 52 ) )

            # setup a path to traverse based on the configured paths
            _path = "{}*/{}".format( self.common.path_start, self.common.path_for_apps )

            # process the images
            self.__process_images( _path )

            self.common.my_print( "info", ( "*" * 52 ) )
            self.common.my_print( "success", "Good to go." )
            self.common.my_print( "info", ( "*" * 52 ) )

        # elseif we are optimizing an account
        elif self.parsed_args.optimize.lower( ) in [ "account", "acct" ]:

            # check if the account arg has been passed or not
            if self.parsed_args.account is None:

                # we need an account specified
                _acct = input( "Please type the account you wish to optimize: [null]" ) or None

            # otherwise it has
            else:

                _acct = self.parsed_args.account

            # if the account is none, throw an error message and exist
            if _acct is None:

                self.common.my_print( "info", ( "*" * 52 ) )
                self.common.my_print( "error", "You must specify the account you wish to optimize." )
                self.common.my_print( "info", ( "*" * 52 ) )
                sys.exit( )

            else:

                self.common.my_print( "info", ( "*" * 52 ) )
                self.common.my_print( "success", "Starting the image processor." )
                self.common.my_print( "info", ( "*" * 52 ) )

                # setup a path to traverse based on the configured paths
                _path = "{}{}/{}".format( self.common.path_start, _acct, self.common.path_for_apps )

                # process the images
                self.__process_images( _path )

                self.common.my_print( "info", ( "*" * 52 ) )
                self.common.my_print( "success", "Good to go." )
                self.common.my_print( "info", ( "*" * 52 ) )

        # elseif we are optimizing an app
        elif self.parsed_args.optimize.lower( ) in [ "application", "app" ]:

            # check if the account arg has been passed or not
            if self.parsed_args.account is None:

                # we need an account specified
                _acct = input( "Please type the account you wish to optimize: [null]" ) or None

            # otherwise it has
            else:

                _acct = self.parsed_args.account

            # check if the application arg has been passed or not
            if self.parsed_args.application is None:

                # we need an account specified
                _app = input( "Please type the application you wish to optimize: [null]" ) or None

            # otherwise it has
            else:

                _app = self.parsed_args.application

            # if the account or app is none, throw an error message and exist
            if None in ( _acct, _app ):

                self.common.my_print( "info", ( "*" * 52 ) )
                self.common.my_print( "error", "You must specify the account and the application you wish to optimize." )
                self.common.my_print( "info", ( "*" * 52 ) )
                sys.exit( )

            # otherwise we can proceed
            else:

                self.common.my_print( "info", ( "*" * 52 ) )
                self.common.my_print( "success", "Starting the image processor." )
                self.common.my_print( "info", ( "*" * 52 ) )

                # setup a path to traverse based on the configured paths
                _path = "{}{}/{}/{}".format( self.common.path_start, _acct, self.common.path_for_apps, _app )

                # process the images
                self.__process_images( _path )

                self.common.my_print( "info", ( "*" * 52 ) )
                self.common.my_print( "success", "Good to go." )
                self.common.my_print( "info", ( "*" * 52 ) )

        # elseif we are optimizing something else
        elif self.parsed_args.optimize.lower( ) == "other":

            # if the paths are not specified, ask for them
            if _paths is None:

                _paths = input( "Please type in the comma-delimited list of paths you would like to optimize: [null]" ) or None

            # if the paths is still none, throw an error message and exist
            if _paths is None:

                self.common.my_print( "info", ( "*" * 52 ) )
                self.common.my_print( "error", "You must specify the paths you wish to optimize." )
                self.common.my_print( "info", ( "*" * 52 ) )
                sys.exit( )

            # otherwise we can proceed
            else:

                # message
                self.common.my_print( "info", ( "*" * 52 ) )
                self.common.my_print( "success", "Starting the image processor." )
                self.common.my_print( "info", ( "*" * 52 ) )

                # get the paths we want to optimize
                _the_paths = _paths.replace( " ", "" ).strip( ).split( "," )

                # create our Threaded Pool
                _t_pool = Pool( self.common.allowed_threads )

                for p in _the_paths:

                    # add the backup to the pool
                    _t_pool.apply_async( self.__process_images, ( p, ) )

                # close up access to the pool
                _t_pool.close( )

                # join the threads to be run
                _t_pool.join( )

                # clean up
                del _t_pool

                # message
                self.common.my_print( "info", ( "*" * 52 ) )
                self.common.my_print( "success", "Good to go." )
                self.common.my_print( "info", ( "*" * 52 ) )

    # process the images
    def __process_images( self, path ):

        # set the full png list
        _full_png_list = glob.glob( "{}/**/*.png".format( path ), recursive = True )

        # set the full jpg list
        _full_jpg_list = glob.glob( "{}/**/*.jpg".format( path ), recursive = True )

        # set the full jpeg list
        _full_jpeg_list = glob.glob( "{}/**/*.jpeg".format( path ), recursive = True )

        # set the full gif list
        _full_gif_list = glob.glob( "{}/**/*.gif".format( path ), recursive = True )

        # set the full webp list
        _full_webp_list = glob.glob( "{}/**/*.webp".format( path ), recursive = True )

        # set the full svg list
        _full_svg_list = glob.glob( "{}/**/*.svg".format( path ), recursive = True )

        # create our Threaded Pool
        _t_pool = Pool( self.common.allowed_threads )

        # png loop
        for p in _full_png_list:

            # add the backup to the pool
            _t_pool.apply_async( self.__process_pngs, ( p, ) )

        # jpg loop
        for p in _full_jpg_list:

            # add the backup to the pool
            _t_pool.apply_async( self.__process_jpgs, ( p, ) )

        # jpeg loop
        for p in _full_jpeg_list:

            # add the backup to the pool
            _t_pool.apply_async( self.__process_jpgs, ( p, ) )

        # gif loop
        for p in _full_gif_list:

            # add the backup to the pool
            _t_pool.apply_async( self.__process_gifs, ( p, ) )

        # webp loop
        for p in _full_webp_list:

            # add the backup to the pool
            _t_pool.apply_async( self.__process_webps, ( p, ) )

        # svg loop
        for p in _full_svg_list:

            # add the backup to the pool
            _t_pool.apply_async( self.__process_svgs, ( p, ) )

        # close up access to the pool
        _t_pool.close( )

        # join the threads to be run
        _t_pool.join( )

        # clean up
        del _t_pool

    # process pngs
    def __process_pngs( self, path ):

        # format the path
        _path = self.common.format_path( path )

        # get the owner user
        _user = self.common.path_owner_user( path )

        # get the owner group
        _group = self.common.path_owner_group( path )

        # optimize the pngs
        _cmd = "optipng -o7 -strip all {}"

        # execute it
        self.common.execute( _cmd.format( _path ) )

        # reset the file's owner and group
        self.common.change_path_ownership( path, _user, _group )

    # process jpgs
    def __process_jpgs( self, path ):

        # format the path
        _path = self.common.format_path( path )

        # get the owner user
        _user = self.common.path_owner_user( path )

        # get the owner group
        _group = self.common.path_owner_group( path )

        # optimize the jpgs
        _cmd = "jpegoptim -o -p --all-progressive --strip-all --max=80 --strip-com --strip-exif --strip-iptc --strip-icc {}"

        # execute
        self.common.execute( _cmd.format( _path ) )

        # reset the file's owner and group
        self.common.change_path_ownership( path, _user, _group )

    # process gifs
    def __process_gifs( self, path ):

        # format the path
        _path = self.common.format_path( path )

        # get the owner user
        _user = self.common.path_owner_user( path )

        # get the owner group
        _group = self.common.path_owner_group( path )

        # optimize the gifs
        _cmd = "gifsicle --batch --optimize=3 {}"

        # execute
        self.common.execute( _cmd.format( _path ) )

        # reset the file's owner and group
        self.common.change_path_ownership( path, _user, _group )

    # process webps
    def __process_webps( self, path ):

        # format the path
        _path = self.common.format_path( path )

        # get the owner user
        _user = self.common.path_owner_user( path )

        # get the owner group
        _group = self.common.path_owner_group( path )

        # setup a command to run
        _cmd = "cwebp -sns 70 -f 100 -q 70 -mt {} -o {}"

        # execute it
        self.common.execute( _cmd.format( _path, _path ) )

        # reset the file's owner and group
        self.common.change_path_ownership( path, _user, _group )

    # process svgs
    def __process_svgs( self, path ):

        # format the path
        _path = self.common.format_path( path )

        # get the owner user
        _user = self.common.path_owner_user( path )

        # get the owner group
        _group = self.common.path_owner_group( path )

        # open the SVG as a XML string
        _xml = open( _path, 'r' ).read( )

        # import the xml minidom parser
        import xml.dom.minidom as dom

        # process the xml string
        _dom = dom.parseString( _xml )
        _out = ''.join( [ line.strip( ) for line in _dom.toxml( ).splitlines( ) ] )
        _dom.unlink( )

        # overwrite the svg with the parsed xml string
        with open( _path, 'w' ) as _outfile:
            _outfile.write( _out )

        # reset the file's owner and group
        self.common.change_path_ownership( path, _user, _group )
