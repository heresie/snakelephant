import pylibs.Settings as Settings
import shutil, os, pycurl
from pylibs.QueueManager import QueueManager as QueueManager

class FileManager(object):

    @staticmethod
    def move_file(url, localfile):
        print "Download complete : %s" % url
        shutil.move(Settings.incomplete_dir + localfile, Settings.complete_dir + localfile)
        os.chmod(Settings.complete_dir + localfile, Settings.default_chmod)

        queue_manager = QueueManager()
        queue_manager.setStatus(url, 3)
        queue_manager.saveQueue()

    @staticmethod
    def sigterm_catcher(url):
        queue_manager = QueueManager()
        current_status = queue_manager.getStatus(url)
        
        if current_status == 3:
            print "Stopping download of : %s" % url
            queue_manager.setStatus(url, 1)
            queue_manager.saveQueue()

    @staticmethod
    def download_file(url, localfile, resume_download = True):
        try:
            print "Starting download of : %s" % url

            queue_manager = QueueManager()
            queue_manager.setStatus(url, 2)
            queue_manager.saveQueue()

            c = pycurl.Curl()
            c.setopt(c.URL, url)
            c.setopt(c.USERAGENT, "SnakElephant 0.1 (Python)")
            c.setopt(c.FOLLOWLOCATION, True)
            c.setopt(c.MAXREDIRS, 5)
            c.setopt(c.CONNECTTIMEOUT, 30)
            c.setopt(c.AUTOREFERER, True)
            c.setopt(c.SSL_VERIFYHOST, False)
            c.setopt(c.SSL_VERIFYPEER, False)

            if resume_download and os.path.isfile(Settings.incomplete_dir + localfile):
                start_existing = os.path.getsize(Settings.incomplete_dir + localfile)
                c.setopt(c.RESUME_FROM, start_existing)
                c.setopt(c.WRITEDATA, open(Settings.incomplete_dir + localfile, "ab"))
            else:
                c.setopt(c.WRITEDATA, open(Settings.incomplete_dir + localfile, "w"))

            c.perform()

            FileManager.move_file(url, localfile)

        except pycurl.error, err:
            if c.getinfo(c.HTTP_CODE) == 416:
                print "Resuming download is not supported by the remote server. Restarting normally."
                FileManager.download_file(url, localfile, False)
                pass
            else:
                queue_manager.setStatus(url, 0)
                queue_manager.saveQueue()
                pass
