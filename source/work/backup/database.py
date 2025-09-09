#!/usr/bin/env python3

# common imports
import time, sys, shutil

# import the threadpool
from multiprocessing.pool import ThreadPool as Pool

class KP_Backup_Database:

    # initialize us
    def __init__( self, db, paths ):

        # we'll need our commmon class in here for some items, so import it now
        from work.common.common import KP_Common

        # let's set the class to a class wide variable so we can use it later on if we need
        self.common = KP_Common( )

        # hold the internal paths
        self.paths = paths

        # hold the database we're backing up
        self.database = db

    # destroyer!
    def __del__( self ):

        # clean up
        del self.common, self.paths

    # get the right db binary
    def get_mysql_binary( self ):
    
        # Check for mariadb first (if you prefer it)
        if shutil.which('mariadb'):
            return 'mariadb'
        elif shutil.which('mysql'):
            return 'mysql'
        else:
            raise Exception("Neither mysql nor mariadb client found in PATH")
        
    # get the right db binary
    def get_mysqldump_binary( self ):
    
        # Check for mariadb first (if you prefer it)
        if shutil.which('mariadb-dump'):
            return 'mariadb-dump'
        elif shutil.which('mysqldump'):
            return 'mysqldump'
        else:
            raise Exception("Neither mysql nor mariadb client found in PATH")

    # run the backup
    def run( self ):

        # if we're backing up all databases
        if self.database.lower( ) == "all":

            # run the all database backup
            self.__run_all_backup( )

        else:

            # run the single database backup
            self.__run_single_backup( self.database )

        # if paths exists
        if self.paths is not None:

            # process the "extra" path(s) backups
            self.common.run_other_backup( self.paths )

    # build out a mysql command to run the backup
    def __mysqldump( self ):

        # hold our command
        _cmd = self.get_mysqldump_binary( ) + " {} --single-transaction --routines --no-create-db "

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

    # setup the database connection: this is currently not in use, however will be in the future
    def __db_connection( self ):

        # we want to catch an exception here
        try:

            # import the mysql module
            import MySQLdb

        # catch the exception here
        except:

            # import the pymysql module as MySQLdb
            import pymysql as MySQLdb

        # hold our db connection handle
        _dbch = None

        # we want to catch an exception here
        try:

            # let's see if we have a defaults file
            if self.common.mysql_defaults:

                # we do, use it to connect
                _dbch = MySQLdb.connect( self.common.mysql_host, read_default_file=self.common.mysql_defaults )
            
            # we don't, so test for a username and password
            elif ( self.common.mysql_user is not None ) and ( self.common.mysql_password is not None ):

                # we do, use them to connect
                _dbch = MySQLdb.connect( self.common.mysql_host, self.common.mysql_user, self.common.mysql_password )

            # we have nothing, so give it a shot.
            else:

                # try to connect without
                _dbch = MySQLdb.connect( self.common.mysql_host )

        # catch the exception here
        except:

            # return none
            return None

        # return the connection handle
        return _dbch

    # run a single databases backup
    def __run_single_backup( self, db ):

        # the main mysqldump command
        _the_command = self.__mysqldump( ) + " {}"

        # setup the destination
        _dest = "{}{}/".format( self.common.backup_path_db, db )

        # the backup command needs to be a bit different than the norm
        _bu_cmd = "{} | {} backup --stdin --stdin-filename {}.sql".format( 
            _the_command.format( db ),
            self.common.primary_command.format( _dest ),
            db
        )

        # initialize if we need to
        self.common.backup_init( _dest )

        # run the backup command
        self.common.execute( _bu_cmd )

        # clean up the backup
        self.common.backup_cleanup( _dest )

    # run all databases backup
    def __run_all_backup( self ):

        # start up the sql command to get all the databases
        _cmd = self.get_mysql_binary( ) + " {} -se 'SHOW DATABASES;'"

        # let's see if we have a defaults file
        if self.common.mysql_defaults:

            # we do, return the string with the defaults file appended
            _cmd = _cmd.format( "--defaults-file={}".format( self.common.mysql_defaults ) )
        
        # we don't, so test for a username and password
        elif ( self.common.mysql_user is not None ) and ( self.common.mysql_password is not None ):

            # we do, return the string with the user and password appended
            _cmd = _cmd.format( "-u {} -p{}".format( self.common.mysql_user, self.common.mysql_password ) )

        # we have nothing, so give it a shot.
        else:

            # return the string with no formatting
            _cmd = _cmd

        # get the list of databases
        _dbs = self.common.execute( _cmd, False )

        # make sure we have a return
        if _dbs:

            # loop the databases
            for _db in _dbs.splitlines( ): #split('\n'):

                # filter our the blank lines
                if not _db: continue
                
                # convert the byte string to a plain string
                _the_db = _db.decode( "utf-8" )

                # make sure it's not a system database
                if _the_db in [ "sys", "mysql", "information_schema", "performance_schema" ]: continue

                # backup the database
                self.__run_single_backup( _the_db )
