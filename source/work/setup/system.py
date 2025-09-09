#!/usr/bin/env python3

# common imports
import time, os, sys

class KP_System_Setup:

    # initialize us
    def __init__( self ):

        # we'll need our commmon class in here for some items, so import it now
        from work.common.common import KP_Common

        # let's set the class to a class wide variable so we can use it later on if we need
        self.common = KP_Common( )

        # setup a local variable for memory calculation
        self.available_memory = 0

        # force us to install psutil
        self.common.execute( "pip3 install --upgrade psutil --break-system-packages --root-user-action=ignore" )

        # now import psutil so we can calculate the total system memory
        import psutil

        # get the system memory as a tuple.  [0] is total memory, [4] is free
        _mem = psutil.virtual_memory( )

        # calculate 1/32 of the total memory in MB
        self.available_memory = round( (_mem[0] / 32) / float( 1<<20 ) )

        # get the total memory of the system
        self.total_sys_memory = _mem[0]

        # clean up
        del _mem

    # destroyer!
    def __del__( self ):

        # clean up the common
        del self.common

        # clean up avaiable mem
        del self.available_memory, self.total_sys_memory

    # setup the system 
    def setup_system( self ):

        # show a quick message
        self.common.my_print( "info", ( "*" * 52 ) )
        self.common.my_print( "success", "Please hold while we setup the system necessities" )
        self.common.my_print( "success", "Please make sure to pay attention, we may ask some questions..." )
        self.common.my_print( "info", ( "*" * 52 ) )

        # setup the system apps
        self.__system_apps( )

        # implement the system tweaks
        self.__tweak_system( )

        # sleep a little
        time.sleep( 5 )

        # show an "all set" message
        self.common.my_print( "info", ( "*" * 52 ) )
        self.common.my_print( "success", "The system is all set" )

        # check if the server needs to be restarted
        if os.path.exists( "/var/run/reboot-required" ):

            # it does, so notify them
            self.common.my_print( "success", "Please note, your system needs to be rebooted." )

        self.common.my_print( "info", ( "*" * 52 ) )

    # install the system apps
    def __system_apps( self ):

        # make sure we update apt's cache
        self.common.execute( "apt-get update" )

        # check if curl is installed, if not, install it
        self.common.execute( "apt-get -y install curl", False )

        # check if restic is installed if not, install it
        self.common.execute( "apt-get -y install restic", False )

        # install pip if it is not currently installed
        self.common.execute( "apt-get -y install python3-pip", False )

        # install the gcc and python3-dev
        self.common.execute( "apt-get -y install gcc python3-dev", False )

        # install python invoke, if it is not currently installed
        self.common.execute( "apt-get -y install python3-invoke", False )

        # libmysqlclient-dev
        self.common.execute( "apt-get -y install libmysqlclient-dev", False )

        # check if the mysql python module is installed
        self.common.execute( "apt-get -y install python3-mysqldb", False )

        # check if the python3 boto module is installed
        self.common.execute( "apt-get -y install python3-boto python3-boto3", False )

        # check if fail2ban is installed, if not install it
        self.common.execute( "apt-get -y install fail2ban", False )

        # check if optipng is installed, if not install it
        self.common.execute( "apt-get -y install optipng jpegoptim gifsicle webp", False )

        # check if inotify-tools is installed, if not install it
        self.common.execute( "apt-get -y install inotify-tools", False )

        # make sure pip is up to date
        self.common.execute( "pip3 install --user --upgrade pip --break-system-packages --root-user-action=ignore", False )

        # install/upgrade python-dateutil module
        self.common.execute( "pip3 install --upgrade python-dateutil --break-system-packages --root-user-action=ignore", False )

        # install/upgrade the enquiries module
        self.common.execute( "pip3 install --upgrade enquiries --break-system-packages --root-user-action=ignore", False )

        # insall/upgrade the requests module
        self.common.execute( "pip3 install --upgrade requests --break-system-packages --root-user-action=ignore", False )


        # insall/upgrade the pymsql module
        self.common.execute( "pip3 install --upgrade pymysql --break-system-packages --root-user-action=ignore", False )


        # check if maldet is installed
        if os.path.exists( "/usr/local/maldetect/maldet" ):

            # it does, so just update it and it's definitions
            self.common.execute( "maldet -u" )
            self.common.execute( "maldet -d" )

        # it's not installed, so let's do that now
        else:

            # get our current directory
            _cur_dir = os.getcwd( )
            
            # set a install path
            _install_path = "/usr/local/src/maldetect-current"

            # download it
            self.common.execute( "wget http://www.rfxn.com/downloads/maldetect-current.tar.gz -P /usr/local/src/" )

            # make a directory to unzip it to, if it does not already exist
            if not os.path.isdir( _install_path ):
                os.mkdir( _install_path )

            # decompress it
            self.common.execute( "tar -xzf /usr/local/src/maldetect-current.tar.gz -C {}".format( _install_path ) )

            self.common.execute( "mv {}/* {}/maldet/".format( _install_path, _install_path ) )

            # change to the directory this is in
            os.chdir( "{}/maldet/".format( _install_path ) )
    
            # run the installer script
            self.common.execute( "bash install.sh" )

            # get back to our originating directory
            os.chdir( _cur_dir )

            # remove the installables
            self.common.execute( "rm -rf {}".format( _install_path ) )

            # now let's make sure we setup our monitoring.
            with open( "/usr/local/maldetect/monitor_paths", 'w' ) as _mon_file:

                # write the start path to monitor
                _mon_file.write( "{}".format( self.common.path_start or "/" ) ) 

            # make sure we allow scanning files owned by root
            self.common.execute( "sed -i 's/scan_ignore_root=\"0\"/scan_ignore_root=\"1\"/g' /usr/local/maldetect/conf.maldet" )

        # clamav has a very high memory usage due to the very nature of the app and it's databases
        # let's make sure the server has at least 2G of ram before installing it
        # installing on a server with less could cause OOM issues
        if self.total_sys_memory > 2056000000:

            # install clamav
            self.common.execute( "apt-get install -y clamav clamav-freshclam" )
        
        # let's check and see if we already wp-cli installed
        if os.path.exists( "/usr/local/bin/wp" ):

            # it is, so let's just run it's updater
            self.common.execute( "wp --allow-root cli update" )
        
        # it's not installed yet, so let's do that now
        else:

            # use curl to download wp-cli
            self.common.execute( "curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar" )
        
            # make it executable
            self.common.execute( "chmod +x wp-cli.phar" )
        
            # move it to the user bin
            self.common.execute( "mv wp-cli.phar /usr/local/bin/wp" )

    # system tweaks
    def __tweak_system( self ):

        # get the path to our limits file
        _path = "/etc/security/limits.conf"

        # delete the original config file, so we can re-create it, just make sure it exists first
        if os.path.isfile( _path ):

            # it does, so delete it
            os.remove( _path )

        # create it
        self.common.execute( "touch {}".format( _path ) )

        # write out new configuration
        with open( _path, "w" ) as _file:
            _file.write( "* - nofile 500000\n" )
            _file.write( "*         hard    nofile      500000\n" )
            _file.write( "*         soft    nofile      500000\n" )
            _file.write( "root      hard    nofile      500000\n" )
            _file.write( "root      soft    nofile      500000\n" )

        # get the path of our system control config
        _path = "/etc/sysctl.conf"

        # delete the original config file, so we can re-create it, just make sure it exists first
        if os.path.isfile( _path ):

            # it does, so delete it
            os.remove( _path )

        # create it
        self.common.execute( "touch {}".format( _path ) )

        # write out new configuration
        with open( _path, "w" ) as _file:
            _file.write( "# -----------------------------------------\n" )
            _file.write( "# ===================================================================\n" )
            _file.write( "# Universal System & Kernel Settings\n" )
            _file.write( "# ===================================================================\n" )
            _file.write( "# Reboot 10 seconds after a kernel panic\n" )
            _file.write( "kernel.panic = 10\n" )
            _file.write( "# System-wide limit for open file descriptors (high for server, overkill but harmless for desktop)\n" )
            _file.write( "fs.file-max = 8388608\n" )
            _file.write( "# Max Asynchronous I/O requests\n" )
            _file.write( "fs.aio-max-nr = 2097152\n" )
            _file.write( "# Max memory map areas per process\n" )
            _file.write( "vm.max_map_count = 524288\n" )
            _file.write( "# Increase max System V IPC message queue sizes\n" )
            _file.write( "kernel.msgmax = 65536\n" )
            _file.write( "kernel.msgmnb = 65536\n" )
            _file.write( "# ===================================================================\n" )
            _file.write( "# Virtual Memory (VM) Settings\n" )
            _file.write( "# ===================================================================\n" )
            _file.write( "# How aggressively to swap.\n" )
            _file.write( "vm.swappiness = 60\n" )
            _file.write( "# Lowering encourages kernel to retain dentry/inode caches.\n" )
            _file.write( "vm.vfs_cache_pressure = 50\n" )
            _file.write( "# Dirty Page Management (Good for NVMe on both)\n" )
            _file.write( "vm.dirty_background_ratio = 5\n" )
            _file.write( "vm.dirty_ratio = 15\n" )
            _file.write( "# Memory Overcommit\n" )
            _file.write( "vm.overcommit_memory = 1\n" )
            _file.write( "# ===================================================================\n" )
            _file.write( "# Core Networking Settings (net.core)\n" )
            _file.write( "# ===================================================================\n" )
            _file.write( "# Max connections in listen queue (high for server, overkill for desktop)\n" )
            _file.write( "net.core.somaxconn = 65535\n" )
            _file.write( "# Max packets queued on network device input\n" )
            _file.write( "net.core.netdev_max_backlog = 65536\n" )
            _file.write( "# Default/Max socket buffer sizes (increased for server, generous for desktop)\n" )
            _file.write( "net.core.rmem_default = 262144\n" )
            _file.write( "net.core.wmem_default = 262144\n" )
            _file.write( "net.core.rmem_max = 33554432\n" )
            _file.write( "net.core.wmem_max = 33554432\n" )
            _file.write( "net.core.optmem_max = 256000\n" )
            _file.write( "# Default packet scheduler\n" )
            _file.write( "net.core.default_qdisc = fq_codel\n" )
            _file.write( "# ===================================================================\n" )
            _file.write( "# IPv4 Networking Settings (net.ipv4)\n" )
            _file.write( "# ===================================================================\n" )
            _file.write( "# --- IP Forwarding & Redirects ---\n" )
            _file.write( "# Essential for the web server/router role.\n" )
            _file.write( "net.ipv4.ip_forward = 1\n" )
            _file.write( "net.ipv4.conf.all.accept_redirects = 0\n" )
            _file.write( "net.ipv4.conf.default.accept_redirects = 0\n" )
            _file.write( "net.ipv4.conf.all.secure_redirects = 0\n" )
            _file.write( "net.ipv4.conf.default.secure_redirects = 0\n" )
            _file.write( "net.ipv4.conf.all.send_redirects = 0\n" )
            _file.write( "net.ipv4.conf.default.send_redirects = 0\n" )
            _file.write( "# --- Security & Anti-Spoofing ---\n" )
            _file.write( "net.ipv4.conf.all.rp_filter = 1\n" )
            _file.write( "net.ipv4.conf.default.rp_filter = 1\n" )
            _file.write( "net.ipv4.conf.all.log_martians = 1\n" )
            _file.write( "net.ipv4.conf.default.log_martians = 1\n" )
            _file.write( "net.ipv4.conf.all.accept_source_route = 0\n" )
            _file.write( "net.ipv4.conf.default.accept_source_route = 0\n" )
            _file.write( "# --- Ephemeral Ports ---\n" )
            _file.write( "net.ipv4.ip_local_port_range = 32768 65535\n" )
            _file.write( "# --- TCP Settings: Congestion Control & General ---\n" )
            _file.write( "net.ipv4.tcp_congestion_control = bbr\n" )
            _file.write( "net.ipv4.tcp_slow_start_after_idle = 0\n" )
            _file.write( "net.ipv4.tcp_timestamps = 1\n" )
            _file.write( "net.ipv4.tcp_sack = 1\n" )
            _file.write( "net.ipv4.tcp_window_scaling = 1\n" )
            _file.write( "net.ipv4.tcp_moderate_rcvbuf = 1\n" )
            _file.write( "net.ipv4.tcp_rfc1337 = 1\n" )
            _file.write( "# Kept at '1' for web server with many transient connections.\n" )
            _file.write( "net.ipv4.tcp_no_metrics_save = 1\n" )
            _file.write( "net.ipv4.tcp_notsent_lowat = 32768\n" )
            _file.write( "net.ipv4.tcp_fastopen = 3\n" )
            _file.write( "net.ipv4.tcp_mtu_probing = 1\n" )
            _file.write( "# --- TCP Settings: SYN Flood Protection & Connection Handling ---\n" )
            _file.write( "net.ipv4.tcp_syncookies = 1\n" )
            _file.write( "# High for server, overkill for desktop\n" )
            _file.write( "net.ipv4.tcp_max_syn_backlog = 32768\n" )
            _file.write( "net.ipv4.tcp_syn_retries = 3\n" )
            _file.write( "net.ipv4.tcp_synack_retries = 2\n" )
            _file.write( "# --- TCP Settings: TIME_WAIT Sockets Management ---\n" )
            _file.write( "# High for server, overkill for desktop\n" )
            _file.write( "net.ipv4.tcp_max_tw_buckets = 2000000\n" )
            _file.write( "net.ipv4.tcp_tw_reuse = 1\n" )
            _file.write( "# Aggressive for server, generally okay for desktop but less critical\n" )
            _file.write( "net.ipv4.tcp_fin_timeout = 15\n" )
            _file.write( "# --- TCP Settings: Keepalive ---\n" )
            _file.write( "net.ipv4.tcp_keepalive_time = 120\n" )
            _file.write( "net.ipv4.tcp_keepalive_intvl = 15\n" )
            _file.write( "net.ipv4.tcp_keepalive_probes = 6\n" )
            _file.write( "# --- TCP Settings: Buffers ---\n" )
            _file.write( "net.ipv4.tcp_rmem = 4096 262144 33554432\n" )
            _file.write( "net.ipv4.tcp_wmem = 4096 131072 33554432\n" )
            _file.write( "# --- UDP Settings ---\n" )
            _file.write( "net.ipv4.udp_rmem_min = 8192\n" )
            _file.write( "net.ipv4.udp_wmem_min = 8192\n" )
            _file.write( "# --- ICMP Settings ---\n" )
            _file.write( "net.ipv4.icmp_echo_ignore_all = 1\n" )
            _file.write( "# --- ARP Cache Tuning (Relevant for router, less so for typical desktop) ---\n" )
            _file.write( "net.ipv4.neigh.default.gc_thresh1 = 512\n" )
            _file.write( "net.ipv4.neigh.default.gc_thresh2 = 2048\n" )
            _file.write( "net.ipv4.neigh.default.gc_thresh3 = 4096\n" )

        # reload the system configuration
        self.common.execute( "sysctl -p" )
