import pylibs.Settings as Settings
import shutil, os, csv, time, pycurl
from pprint import pprint

class QueueManager(object):
    def __init__(self):
        self.modified = False
        self.loadQueue()

    def __del__(self):
        self.saveQueue()

    def loadQueue(self):
        try:
            self.queue_data = [ ]

            queue_data = csv.reader(open(Settings.queue_file, 'rb'), delimiter=Settings.queue_delimiter)
            
            for queue_task in queue_data:
                queue_task.insert(Settings.QINDEX_SPEED, 0)
                queue_task.insert(Settings.QINDEX_PERCENT, 0)
                self.queue_data.append(queue_task)

        except IOError:
            print 'Error opening queue file %s' % Settings.queue_file
            exit()

    def saveQueue(self):
        try:
            if self.modified == True:
                queue_writer = csv.writer(open(Settings.queue_file, 'w'), delimiter=Settings.queue_delimiter)

                for queue_task in self.queue_data:
                    queue_writer.writerow(queue_task)

                self.modified = False

        except IOError:
            print 'Error saving queue file %s' % Settings.queue_file
            exit()

    def addQueue(self, url):
        try:
            url = url.replace(' ', '%20')

            if self.isQueued(url) == True:
                return False

            file_infos = self.getRemoteDatas(url)
            file_infos.insert(Settings.QINDEX_STATUS, 0)
            file_infos.insert(Settings.QINDEX_DOWNLOADED, 0)
            file_infos.insert(Settings.QINDEX_SPEED, 0)
            file_infos.insert(Settings.QINDEX_PERCENT, 0)
            file_infos.insert(Settings.QINDEX_TIMESTAMP_START, 0)

            self.queue_data.append(file_infos)

            self.modified = True

            return True

        except IOError:
            print 'Error occured in addQueue method'
            pass

    def delQueue(self, url):
        try:
            if self.isQueued(url) == False:
               return False

            for queue_task in self.queue_data:
                  if queue_task[Settings.QINDEX_URL] == url:
                      self.queue_data.remove(queue_task) 
                      self.Modified = True

            return True

        except IOError:
            print 'Error occured in delQueue method'
            pass

    def checkStatus(self, url, verbose = False):
        if self.isQueued(url) == False:
            return False

        file_infos = [ ]
        queue_index = 0        

        for queue_task in self.queue_data:
            if queue_task[Settings.QINDEX_URL] == url:
                file_infos = queue_task
                queue_index = self.queue_data.index(queue_task)

        if int(file_infos[Settings.QINDEX_STATUS]) < 3:
            file_path = Settings.incomplete_dir + file_infos[Settings.QINDEX_FILE]
        else:
            file_path = Settings.complete_dir + file_infos[Settings.QINDEX_FILE]

        try:
            file_infos[Settings.QINDEX_DOWNLOADED] = os.path.getsize(file_path)
        except OSError:
            file_infos[Settings.QINDEX_DOWNLOADED] = 0

        if int(file_infos[Settings.QINDEX_STATUS]) == 3:
            file_infos[Settings.QINDEX_PERCENT] = "%.2f" % 100
            file_infos[Settings.QINDEX_DOWNLOADED] = file_infos[Settings.QINDEX_SIZE]
            file_infos[Settings.QINDEX_SPEED] = "%.2f b/s" % 0
        else:
            file_infos[Settings.QINDEX_PERCENT] = "%.2f" % ((int(file_infos[Settings.QINDEX_DOWNLOADED]) * 100) / int(file_infos[Settings.QINDEX_SIZE]))

            delta_time = int(time.time()) - int(file_infos[Settings.QINDEX_TIMESTAMP_START])
                        
            if delta_time != 0:
                file_infos[Settings.QINDEX_SPEED] = self.humanReadableSpeed(int(file_infos[Settings.QINDEX_DOWNLOADED]) / (int(time.time()) - int(file_infos[Settings.QINDEX_TIMESTAMP_START])))
            else:
                file_infos[Settings.QINDEX_SPEED] = self.humanReadableSpeed(0)
                

        if verbose == True:
            print "url               : " + file_infos[Settings.QINDEX_URL]
            print "file              : " + file_infos[Settings.QINDEX_FILE]
            print "type              : " + file_infos[Settings.QINDEX_TYPE]
            print "size              : " + str(file_infos[Settings.QINDEX_SIZE])
            print "downloaded        : " + str(file_infos[Settings.QINDEX_DOWNLOADED])
            print "status            : " + str(file_infos[Settings.QINDEX_STATUS])
            print "timestamp_start   : " + str(file_infos[Settings.QINDEX_TIMESTAMP_START])
            print "speed             : " + str(file_infos[Settings.QINDEX_SPEED])
            print "percent           : " + str(file_infos[Settings.QINDEX_PERCENT])
            print ""

        self.queue_data[queue_index] = file_infos

        return file_infos

    def getQueue(self):
        return self.queue_data

    def checkStatuses(self, verbose = False):
        statuses = [ ]

        for queue_task in self.queue_data:
            statuses.append(self.checkStatus(queue_task[Settings.QINDEX_URL], verbose))

        return statuses

    def isQueued(self, url, status = None):
        for queue_task in self.queue_data:
            if status != None and queue_task[Settings.QINDEX_URL] == url and queue_task[Settings.QINDEX_STATUS] == status:
                return True
            elif status == None and queue_task[Settings.QINDEX_URL] == url:
                return True

        return False

    def setStatus(self, url, status):
        if self.isQueued(url) == False:
            return False

        for queue_task in self.queue_data:
            if queue_task[Settings.QINDEX_URL] == url:
                index = self.queue_data.index(queue_task)
                
                self.queue_data[index][Settings.QINDEX_STATUS] = status
                
                if status == 2:
                    self.queue_data[index][Settings.QINDEX_TIMESTAMP_START] = int(time.time())
                
                self.modified = True
                return True

    def getStatus(self, url):
        if self.isQueued(url) == False:
            return False

        for queue_task in self.queue_data:
            if queue_task[Settings.QINDEX_URL] == url:
                return queue_task[Settings.QINDEX_STATUS]

    def getRemoteDatas(self, url):
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.USERAGENT, "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11")
        c.setopt(c.FOLLOWLOCATION, True)
        c.setopt(c.HEADER, False)
        c.setopt(c.NOBODY, True)
        c.setopt(c.SSL_VERIFYHOST, False)
        c.setopt(c.SSL_VERIFYPEER, False)
        c.perform()

        queue_task = [ ]
        queue_task.insert(Settings.QINDEX_URL, c.getinfo(c.EFFECTIVE_URL))
        queue_task.insert(Settings.QINDEX_FILE, os.path.basename(c.getinfo(c.EFFECTIVE_URL)).replace('%20', ' '))
        queue_task.insert(Settings.QINDEX_TYPE, c.getinfo(c.CONTENT_TYPE))
        queue_task.insert(Settings.QINDEX_SIZE, int(c.getinfo(c.CONTENT_LENGTH_DOWNLOAD)))

        return queue_task

    def humanReadableSpeed(self, size):
        k_bytes = size / 1024
        if k_bytes < 1: return "%.2f b/s" % size
 
        m_bytes = k_bytes / 1024
        if m_bytes < 1: return "%.2f kb/s" % k_bytes

        g_bytes = m_bytes / 1024
        if g_bytes < 1: return "%.2f mb/s" % m_bytes

        p_bytes = g_bytes / 1024
        if p_bytes < 1: return "%.2f gb/s" % g_bytes

        return size
