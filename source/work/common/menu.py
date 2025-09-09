#!/usr/bin/env python3

# common imports
import json, boto3, os, sys, time
from datetime import datetime as dt
import dateutil.parser

# import the simple menu module
from simple_term_menu import TerminalMenu

# the menu class
class KP_Menu:

    # initialize us
    def __init__( self, _args = None ):

        # we'll need our commmon class in here for some items, so import it now
        from work.common.common import KP_Common

        # let's set the class to a class wide variable so we can use it later on if we need
        self.common = KP_Common( )

    # destroyer!
    def __del__( self ):

        # clean up the common
        del self.common

    # generate the repo menu
    def repo_menu( self, _repo ):

        # setup the restic command we need to run
        _cmd = self.common.primary_command.format( "{} snapshots --json".format( _repo ) )

        # run the command and get the output
        _snapshots = self.common.execute( _cmd, False )

        # let's process the json response
        _resp = json.loads( _snapshots.decode( "utf-8" ) )

        # hold the menu list
        _mlist = []

        # loop over the json
        for _item in _resp:

            # convert the string to a datetime object
            _parsed_dt = dateutil.parser.parse( _item['time'] )

            # set the formatted date/time
            _dt = _parsed_dt.strftime( "%m/%d/%Y %H:%M:%S" )

            # append the parsed time to the selected list            
            _mlist.append( "{}|{}".format( _dt, _item['short_id'] ) )

        # return the generated menu
        return self.__menu( _mlist, "Select the snapshot to restore:" )


    # generate the database menu
    def database_menu( self ):

        # first we need to select an account
        _s3 = boto3.client( "s3", endpoint_url="https://{}".format( self.common.endpoint ) )

        # check the bucket and path for the selected backup type
        _acct_resp = _s3.list_objects_v2(
                Bucket=self.common.bucket,
                Prefix ='{}/{}'.format( self.common.name, "database/" ),
                Delimiter="/" )

        # we don't need the client anymore
        del _s3

        # the returned account list
        _database_list = [ os.path.basename( os.path.dirname( i["Prefix"] ) ) for i in _acct_resp.get( 'CommonPrefixes', [] ) ]

        # return the generated menu
        return self.__menu( _database_list, "Select the database to restore:" )

    # generate the application menu
    def app_menu( self ):

        # first we need to select an account
        _s3 = boto3.client( "s3", endpoint_url="https://{}".format( self.common.endpoint ) )

        # check the bucket and path for the selected backup type
        _acct_resp = _s3.list_objects_v2(
                Bucket=self.common.bucket,
                Prefix ='{}/{}'.format( self.common.name, "apps/" ),
                Delimiter="/" )

        # we don't need the client anymore
        del _s3

        # the returned account list
        _acct_list = [ os.path.basename( os.path.dirname( i["Prefix"] ) ) for i in _acct_resp.get( 'CommonPrefixes', [] ) ]

        # get the selected account
        _selected_account = self.__menu( _acct_list, "Select the account to restore:" )

        # now that we have the account, select the application
        _s3 = boto3.client( "s3", endpoint_url="https://{}".format( self.common.endpoint ) )

        # get the response for the app to be selected
        _app_resp = _s3.list_objects_v2(
            Bucket=self.common.bucket,
            Prefix='{}/{}{}/'.format( self.common.name, "apps/", _selected_account ),
            Delimiter="/" )

        # we don't need the client anymore
        del _s3

        # build out a list of the accounts we're after here
        _app_list = [ os.path.basename( os.path.dirname( i["Prefix"] ) ) for i in _app_resp.get( 'CommonPrefixes', [] ) ]

        # get the selected application
        _selected_application = self.__menu( _app_list, "Select the application to restore:" )

        # return the account and application as a list
        return [ _selected_account, _selected_application ]

    # restore method menu
    def restore_method_menu( self ):

        # return it
        return self.__menu( [ "Automatic", "Manual", "Browse" ], "How would you like to restore? " )

    # get the backup type menu
    def backup_type_menu( self ):

        # return it
        return self.__menu( [ "Application", "Database", "Other" ], "Select the type of backup you want to restore: " )
    
    # get the location menu
    def location_menu( self ):

        # return it
        return self.__menu( [ "Local", "Remote" ], "Select the location of the original backup: " )

    # show the menu and return the selected value
    def __menu( self, the_list, the_title ):

        # wrap the menu in a try block
        try:

            # the menu
            _menu = TerminalMenu( the_list, 
                title=the_title, 
                search_key=None, 
                show_search_hint=True, 
                show_shortcut_hints=True,
                search_highlight_style={ 'bg_black', 'fg_green' } )

            # show the menu
            _show = _menu.show( )

            # return the selected item
            return the_list[ _show ] or None

        # catch the keyboard interrupt
        except:

            # show a message then exit
            print()
            self.common.my_print( "info", ( "*" * 52 ) )
            self.common.my_print( "success", "Exitting the app, please hold." )
            self.common.my_print( "info", ( "*" * 52 ) )
            time.sleep( 5 )
            sys.exit( )

