import ConfigParser, base64

configuration_file = 'snakelephant.ini'

QINDEX_URL = 0
QINDEX_FILE = 1
QINDEX_TYPE = 2
QINDEX_SIZE = 3
QINDEX_DOWNLOADED = 4
QINDEX_STATUS = 5
QINDEX_TIMESTAMP_START = 6
QINDEX_SPEED = 7
QINDEX_PERCENT = 8
QINDEX_DELTA_DOWNLOADED = 9

try:
    config = ConfigParser.RawConfigParser()
    config.read(configuration_file)

    complete_dir = config.get('downloads', 'complete_dir')
    incomplete_dir = config.get('downloads', 'incomplete_dir')
    queue_file = config.get('queue', 'file')
    queue_delimiter = config.get('queue', 'delimiter')
    queue_max_workers = int(config.get('queue', 'workers'))
    default_chmod = int(config.get('queue', 'default_chmod'))
    server_port = int(config.get('webserver', 'port'))
    root_path = config.get('webserver', 'root_path')
    log_dir = config.get('webserver', 'log_dir')
    web_username = config.get('webserver', 'web_username')
    web_password = config.get('webserver', 'web_password')
    web_credentials = base64.b64encode(web_username + ':' + web_password)

    print "Current configuration from %s" % configuration_file
    print "==================================================="
    print "complete_dir      : %s" % complete_dir
    print "incomplete_dir    : %s" % incomplete_dir
    print "queue_file        : %s" % queue_file
    print "queue_delimiter   : %s" % queue_delimiter
    print "queue_max_workers : %s" % queue_max_workers
    print "default_chmod     : %s" % default_chmod
    print "server_port       : %s" % server_port
    print "root_path         : %s" % root_path
    print "log_dir           : %s" % log_dir
    print "web_username      : %s" % web_username
    print "web_credentials   : %s" % web_credentials
    print ""

except IOError:
    print 'Configuration file not found %s' % configuration_file
    exit()

except ConfigParser.NoSectionError:
    print 'Error in reading configuration file %s' % configuration_file
    exit()
