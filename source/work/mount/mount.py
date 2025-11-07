#!/usr/bin/env python3

# common imports
import os, sys, time, subprocess, signal

class KP_Mount:

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

        # default mount point if not specified
        self.default_mount_path = "/tmp/backup-mount/"

    # destroyer!
    def __del__( self ):

        # clean up the common
        del self.common, self.parsed_args, self.args, self.default_mount_path

    # do what we need to do here
    def run( self ):

        # check if --unmount flag is passed to unmount a path
        if self.parsed_args.unmount:
            self.__unmount_path( self.parsed_args.unmount )
            return

        # check if --list flag is passed to list active mounts
        if self.parsed_args.list_mounts:
            self.__list_active_mounts( )
            return

        # set environment variables for S3 access
        os.environ["AWS_ACCESS_KEY_ID"] = self.common.key
        os.environ["AWS_SECRET_ACCESS_KEY"] = self.common.secret
        os.environ["AWS_DEFAULT_REGION"] = self.common.region
        os.environ["RESTIC_PASSWORD"] = self.common.hash

        # check if we have CLI arguments for source and destination
        if self.parsed_args.source and self.parsed_args.destination:
            
            # use CLI arguments directly (automation mode)
            _repo_path = self.parsed_args.source
            _mount_point = self.parsed_args.destination
            
            # validate that the source path looks like a valid repo path
            if not _repo_path.startswith("s3://"):
                # if it's not an S3 path, prepend the default repo prefix
                _repo_path = "{}{}".format(self.common.backup_repo_prefix, _repo_path)
            
        else:
            # interactive mode - use menus
            
            # import our menu
            from work.common.menu import KP_Menu
            
            # fire up the menu class
            _menu = KP_Menu( )

            # ask what type of backup to mount
            _bu_type = _menu.backup_type_menu( )

            # build the repo path based on the backup type
            if _bu_type.lower( ) == "application":
                
                # get the account and app from menu
                _app = _menu.app_menu( )
                
                # construct the repo path for the application
                _repo_path = "{}apps/{}/{}".format( 
                    self.common.backup_repo_prefix,
                    _app[0],  # account
                    _app[1]   # application
                )

            elif _bu_type.lower( ) == "database":
                
                # get the database from menu
                _database = _menu.database_menu( )
                
                # construct the repo path for the database
                _repo_path = "{}database/{}".format( 
                    self.common.backup_repo_prefix,
                    _database
                )

            elif _bu_type.lower( ) == "other":
                
                # for "other" backups, ask for the specific path
                self.common.my_print( "info", "Please enter the path you backed up that you wish to mount." )
                _bu_path = input( "Path: [null] " ) or None
                
                # validate the path was provided
                if _bu_path is None:
                    self.common.my_print( "info", ( "*" * 52 ) )
                    self.common.my_print( "error", "You must enter a path to mount." )
                    self.common.my_print( "info", ( "*" * 52 ) )
                    sys.exit( )
                
                # construct the repo path for other backups
                _repo_path = "{}other{}".format( 
                    self.common.backup_repo_prefix,
                    _bu_path
                )

            # ask for mount point or use CLI argument if provided
            if self.parsed_args.destination:
                _mount_point = self.parsed_args.destination
            else:
                # ask for mount point interactively
                _mount_point = input( "Please type in a mount point path: [{}]".format( self.default_mount_path ) ) or self.default_mount_path

        # check if mount point is already in use
        if self.__is_mount_point_active( _mount_point ):
            self.common.my_print( "info", ( "*" * 52 ) )
            self.common.my_print( "error", "Mount point {} is already in use!".format( _mount_point ) )
            self.common.my_print( "info", "Please unmount it first with: kp mount --unmount {}".format( _mount_point ) )
            self.common.my_print( "info", ( "*" * 52 ) )
            sys.exit( )

        # create the mount point directory if it doesn't exist
        self.common.execute( "mkdir -p {} && chmod -R 755 {}".format( _mount_point, _mount_point ) )

        # check if we should run in foreground mode (blocking)
        if self.parsed_args.foreground:
            # run in foreground mode (original behavior with CTRL-C)
            self.__mount_foreground( _repo_path, _mount_point )
        else:
            # run in background mode (default)
            self.__mount_background( _repo_path, _mount_point )

        # cleanup environment variables
        self.__cleanup_env_vars( )

    # mount in foreground mode (blocks until CTRL-C)
    def __mount_foreground( self, repo_path, mount_point ):
        
        # construct the restic mount command
        _mount_cmd = self.common.primary_command.format( "{} mount {}".format( repo_path, mount_point ) )

        # show information about the mount
        self.common.my_print( "info", ( "*" * 52 ) )
        self.common.my_print( "info", "Mounting backup repository to:" )
        self.common.my_print( "success", mount_point )
        self.common.my_print( "info", "Repository: {}".format( repo_path ) )
        self.common.my_print( "info", ( "*" * 52 ) )
        self.common.my_print( "info", "FOREGROUND MODE: Mount will remain active while this process runs." )
        self.common.my_print( "info", "Press CTRL-C to unmount and exit." )
        self.common.my_print( "info", ( "*" * 52 ) )

        # try to catch the keyboard interrupt
        try:
            # execute the mount command (this will block until interrupted)
            self.common.execute( _mount_cmd )

        except KeyboardInterrupt:
            # show unmounting message
            print( )
            self.common.my_print( "info", ( "*" * 52 ) )
            self.common.my_print( "info", "Unmounting backup repository..." )
            self.common.my_print( "success", "Mount point has been unmounted." )
            self.common.my_print( "info", ( "*" * 52 ) )

    # mount in background mode (non-blocking, requires manual unmount)
    def __mount_background( self, repo_path, mount_point ):
        
        # construct the restic mount command with nohup for background execution
        _mount_cmd = self.common.primary_command.format( "{} mount {}".format( repo_path, mount_point ) )
        
        # create a log file for the mount process
        _log_file = "/tmp/kp-mount-{}.log".format( os.path.basename( mount_point ).replace("/", "_") )
        
        # start the mount process in the background
        try:
            # use subprocess.Popen to run in background
            _process = subprocess.Popen(
                _mount_cmd,
                shell=True,
                stdout=open(_log_file, 'w'),
                stderr=subprocess.STDOUT,
                preexec_fn=os.setsid,  # create new session to detach from terminal
                env=os.environ.copy()  # pass environment variables
            )
            
            # wait a moment to check if mount was successful
            time.sleep(3)
            
            # check if the mount point is actually mounted
            if self.__is_mount_point_active( mount_point ):
                
                # save mount info for later reference
                self.__save_mount_info( mount_point, repo_path, _process.pid )
                
                # show success message with unmount instructions
                self.common.my_print( "info", ( "*" * 52 ) )
                self.common.my_print( "success", "Backup repository successfully mounted!" )
                self.common.my_print( "info", ( "*" * 52 ) )
                self.common.my_print( "info", "Mount Point: {}".format( mount_point ) )
                self.common.my_print( "info", "Repository: {}".format( repo_path ) )
                self.common.my_print( "info", "Process ID: {}".format( _process.pid ) )
                self.common.my_print( "info", "Log File: {}".format( _log_file ) )
                self.common.my_print( "info", ( "*" * 52 ) )
                self.common.my_print( "info", "IMPORTANT: This mount is running in the BACKGROUND" )
                self.common.my_print( "info", ( "*" * 52 ) )
                self.common.my_print( "info", "To unmount, use one of these commands:" )
                self.common.my_print( "success", "  kp mount --unmount {}".format( mount_point ) )
                self.common.my_print( "success", "  umount {}".format( mount_point ) )
                self.common.my_print( "success", "  fusermount -u {}".format( mount_point ) )
                self.common.my_print( "info", ( "*" * 52 ) )
                self.common.my_print( "info", "To list all active mounts:" )
                self.common.my_print( "success", "  kp mount --list" )
                self.common.my_print( "info", ( "*" * 52 ) )
                
            else:
                # mount failed
                self.common.my_print( "info", ( "*" * 52 ) )
                self.common.my_print( "error", "Mount failed! Check the log file: {}".format( _log_file ) )
                self.common.my_print( "info", ( "*" * 52 ) )
                
                # try to kill the process if it's still running
                try:
                    os.killpg(os.getpgid(_process.pid), signal.SIGTERM)
                except:
                    pass
                
        except Exception as e:
            self.common.my_print( "info", ( "*" * 52 ) )
            self.common.my_print( "error", "Failed to mount repository: {}".format( str(e) ) )
            self.common.my_print( "info", ( "*" * 52 ) )

    # check if a mount point is currently active
    def __is_mount_point_active( self, mount_point ):
        
        # use the mount command to check if path is mounted
        _check_cmd = "mount | grep -q ' {} '".format( mount_point.rstrip('/') )
        
        # run the command and check return code
        _result = subprocess.call( _check_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL )
        
        # return True if mounted (exit code 0), False otherwise
        return _result == 0

    # unmount a specific path
    def __unmount_path( self, mount_point ):
        
        self.common.my_print( "info", ( "*" * 52 ) )
        self.common.my_print( "info", "Attempting to unmount: {}".format( mount_point ) )
        
        # check if the path is actually mounted
        if not self.__is_mount_point_active( mount_point ):
            self.common.my_print( "error", "Path is not currently mounted: {}".format( mount_point ) )
            self.common.my_print( "info", ( "*" * 52 ) )
            return
        
        # try different unmount methods
        unmount_methods = [
            "fusermount -u {}".format( mount_point ),  # FUSE unmount (preferred for restic)
            "umount {}".format( mount_point ),          # standard unmount
            "umount -l {}".format( mount_point )        # lazy unmount as last resort
        ]
        
        # try each unmount method
        for method in unmount_methods:
            _result = subprocess.call( method, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL )
            if _result == 0:
                # unmount successful
                self.common.my_print( "success", "Successfully unmounted: {}".format( mount_point ) )
                
                # clean up mount info file
                self.__cleanup_mount_info( mount_point )
                
                self.common.my_print( "info", ( "*" * 52 ) )
                return
        
        # if we get here, unmount failed
        self.common.my_print( "error", "Failed to unmount. You may need to run as root or use:" )
        self.common.my_print( "info", "  sudo umount -l {}".format( mount_point ) )
        self.common.my_print( "info", ( "*" * 52 ) )

    # list all active restic mounts
    def __list_active_mounts( self ):
        
        self.common.my_print( "info", ( "*" * 52 ) )
        self.common.my_print( "info", "Active Restic Mounts:" )
        self.common.my_print( "info", ( "*" * 52 ) )
        
        # get list of mounts containing 'restic'
        _list_cmd = "mount | grep 'restic\\|backup-mount'"
        
        try:
            _output = subprocess.check_output( _list_cmd, shell=True, stderr=subprocess.DEVNULL )
            _mounts = _output.decode('utf-8').strip().split('\n')
            
            if _mounts and _mounts[0]:
                for mount in _mounts:
                    # parse mount line to extract mount point
                    parts = mount.split(' on ')
                    if len(parts) >= 2:
                        mount_point = parts[1].split(' type')[0]
                        self.common.my_print( "success", "  {}".format( mount_point ) )
                
                self.common.my_print( "info", ( "*" * 52 ) )
                self.common.my_print( "info", "To unmount any of these, run:" )
                self.common.my_print( "info", "  kp mount --unmount <mount_point>" )
            else:
                self.common.my_print( "info", "No active mounts found." )
                
        except subprocess.CalledProcessError:
            self.common.my_print( "info", "No active mounts found." )
        
        self.common.my_print( "info", ( "*" * 52 ) )

    # save mount information for later reference
    def __save_mount_info( self, mount_point, repo_path, pid ):
        
        # create directory for mount info if it doesn't exist
        _info_dir = "/tmp/kp-mounts"
        os.makedirs( _info_dir, exist_ok=True )
        
        # create info file for this mount
        _info_file = "{}/{}.info".format( _info_dir, os.path.basename( mount_point ).replace("/", "_") )
        
        # write mount information
        with open( _info_file, 'w' ) as f:
            f.write( "mount_point={}\n".format( mount_point ) )
            f.write( "repo_path={}\n".format( repo_path ) )
            f.write( "pid={}\n".format( pid ) )
            f.write( "timestamp={}\n".format( time.strftime("%Y-%m-%d %H:%M:%S") ) )

    # cleanup mount info file
    def __cleanup_mount_info( self, mount_point ):
        
        _info_file = "/tmp/kp-mounts/{}.info".format( os.path.basename( mount_point ).replace("/", "_") )
        
        if os.path.exists( _info_file ):
            try:
                os.remove( _info_file )
            except:
                pass

    # cleanup environment variables
    def __cleanup_env_vars( self ):
        
        # cleanup environment variables
        if 'AWS_ACCESS_KEY_ID' in os.environ:
            del os.environ['AWS_ACCESS_KEY_ID']
        if 'AWS_SECRET_ACCESS_KEY' in os.environ:
            del os.environ['AWS_SECRET_ACCESS_KEY']
        if 'AWS_DEFAULT_REGION' in os.environ:
            del os.environ['AWS_DEFAULT_REGION']
        if 'RESTIC_PASSWORD' in os.environ:
            del os.environ['RESTIC_PASSWORD']