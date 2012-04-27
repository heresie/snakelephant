import pylibs.Settings as Settings
import string, cgi, time, json
from os import sep, curdir, pardir, statvfs
from urlparse import parse_qs
from BaseHTTPServer import BaseHTTPRequestHandler
from pylibs.QueueManager import QueueManager as QueueManager

class WebServer(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        open(Settings.log_dir + 'access.log', 'a+').write("%s - - [%s] %s\n" % (self.address_string(), self.log_date_time_string(), format%args))

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm=\"Test\"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
    def do_GET(self):
        authed = False
        try:
            if self.headers.getheader('Authorization') == None:
                self.do_AUTHHEAD()
                self.wfile.write('no auth header received')
                pass
            elif self.headers.getheader('Authorization') == 'Basic %s' % Settings.web_credentials:
                authed = True
                pass
            else:
                self.wfile.write('not authenticated')
                pass
            
            if (authed == False):
                return
            
            # Verification des telechargements
            if self.path.startswith('/check-dl'):
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()

                queue_manager = QueueManager()
                queue_status = queue_manager.checkStatuses()

                total_space = statvfs(Settings.complete_dir).f_files * statvfs(Settings.complete_dir).f_bsize / 1024 / 1024 / 1024
                free_space = statvfs(Settings.complete_dir).f_bavail * statvfs(Settings.complete_dir).f_bsize / 1024 / 1024 / 1024

                self.wfile.write(json.dumps([[free_space, total_space], queue_status]))
                
                return

            # Ajout d'un DL
            if self.path.startswith('/add-url'):
                fileURL = ''
                qspos = self.path.find('?')
                if qspos >= 0:
                    qs = parse_qs(self.path[qspos+1:], keep_blank_values=1)
                    if 'fileURL' in qs:
                        fileURL = qs['fileURL'][0]

                queue_manager = QueueManager()
                queue_manager.addQueue(fileURL)

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                return

            # Default handler
            if (self.path == '/'): 
                self.path = '/manager.html'

            f = open(Settings.root_path + sep + self.path)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(f.read())
            f.close()

            return
                
        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)