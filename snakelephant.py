#!/usr/bin/python

import pylibs.Settings as Settings
import socket, threading, time
from pylibs.QueueManager import QueueManager as QueueManager
from pylibs.FileManager import FileManager as FileManager
from pylibs.WebServer import WebServer as WebServer
from multiprocessing import Process
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

def main():

    workers = [ ]

    try:
        server = HTTPServer(('', Settings.server_port), WebServer)

        print "Starting WebServer on %s" % Settings.server_port
        webserver_process = Process(name='webserver', target=server.serve_forever)
        webserver_process.start()
        workers.append(webserver_process)

    except socket.error:
        print 'WebServer port already taken : %s in use' % Settings.server_port
        exit()

    while True:
        try:
            queue_manager = QueueManager()
            queue_data = queue_manager.getQueue()

            for queue_task in queue_data:
                if int(queue_task[Settings.QINDEX_STATUS]) < 2:
                    dl_process = Process(name=queue_task[Settings.QINDEX_URL], target=FileManager.download_file, args=(queue_task[Settings.QINDEX_URL], queue_task[Settings.QINDEX_FILE]))
                    dl_process.start()
                    workers.append(dl_process)

            time.sleep(5)

        except KeyboardInterrupt:
            print " Interrupt caught : stopping program"
            for worker in workers:
                if worker.name.startswith('webserver'):
                    print 'Stopping WebServer'
                    server.socket.close()
                else:
                    FileManager.sigterm_catcher(worker.name)

                worker.terminate()
                worker.join()
            break

if __name__ == '__main__':
    main()
