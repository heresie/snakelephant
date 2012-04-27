import pylibs.Settings as Settings
import string, cgi, time, json
from os import sep, curdir, pardir
from urlparse import parse_qs, urlparse
from BaseHTTPServer import BaseHTTPRequestHandler
from pylibs.QueueManager import QueueManager as QueueManager

class WebServer(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        open(Settings.log_dir + 'access.log', 'a+').write("%s - - [%s] %s\n" % (self.address_string(), self.log_date_time_string(), format%args))

    def do_GET(self):
        try:
            # Verification des telechargements
            if self.path.startswith('/check-dl'):
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()

                queue_manager = QueueManager()
                queue_status = queue_manager.checkStatuses()

                self.wfile.write(json.dumps(queue_status))
                
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